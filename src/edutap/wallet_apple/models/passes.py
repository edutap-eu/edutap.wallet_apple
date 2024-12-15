from collections import OrderedDict
from pathlib import Path
from edutap.wallet_apple import crypto
from enum import Enum
from io import BytesIO
from pydantic import BaseModel
from pydantic import computed_field
from pydantic import Field as PydanticField
from pydantic.fields import FieldInfo
from typing import Any, Dict
from typing import Optional
from typing_extensions import deprecated

import base64
import functools
import hashlib
import json
import typing
import zipfile


def bytearray_to_base64(bytearr):
    encoded_data = base64.b64encode(bytearr)
    return encoded_data.decode("utf-8")


def base64_to_bytearray(base64_str):
    decoded_data = base64.b64decode(base64_str)
    return decoded_data


class Alignment(Enum):
    LEFT = "PKTextAlignmentLeft"
    CENTER = "PKTextAlignmentCenter"
    RIGHT = "PKTextAlignmentRight"
    JUSTIFIED = "PKTextAlignmentJustified"
    NATURAL = "PKTextAlignmentNatural"


class BarcodeFormat(Enum):
    PDF417 = "PKBarcodeFormatPDF417"
    QR = "PKBarcodeFormatQR"
    AZTEC = "PKBarcodeFormatAztec"
    CODE128 = "PKBarcodeFormatCode128"


# Barcode formats that are supported by iOS 6 and 7
legacy_barcode_formats = [BarcodeFormat.PDF417, BarcodeFormat.QR, BarcodeFormat.AZTEC]


class TransitType(Enum):
    AIR = "PKTransitTypeAir"
    TRAIN = "PKTransitTypeTrain"
    BUS = "PKTransitTypeBus"
    BOAT = "PKTransitTypeBoat"
    GENERIC = "PKTransitTypeGeneric"


class DateStyle(Enum):
    NONE = "PKDateStyleNone"
    SHORT = "PKDateStyleShort"
    MEDIUM = "PKDateStyleMedium"
    LONG = "PKDateStyleLong"
    FULL = "PKDateStyleFull"


class NumberStyle(Enum):
    DECIMAL = "PKNumberStyleDecimal"
    PERCENT = "PKNumberStylePercent"
    SCIENTIFIC = "PKNumberStyleScientific"
    SPELLOUT = "PKNumberStyleSpellOut"


class Field(BaseModel):
    key: str  # Required. The key must be unique within the scope
    value: str | int | float  # Required. Value of the field. For example, 42
    label: str = ""  # Optional. Label text for the field.
    changeMessage: str = ""  # Optional. Format string for the alert text that is displayed when the pass is updated
    # textAlignment: Alignment = Alignment.LEFT
    textAlignment: Alignment | None = None
    # Optional. Alignment for the field’s contents
    # textAlignment: MyEnum | None = None  # Optional. Alignment for the field’s contents


class DateField(Field):
    dateStyle: DateStyle = DateStyle.SHORT
    timeStyle: DateStyle = DateStyle.SHORT
    isRelative: bool = False
    ignoresTimeZone: bool = False


class NumberField(Field):
    numberStyle: NumberStyle = NumberStyle.DECIMAL


class CurrencyField(Field):
    currencyCode: str = "USD"


class Barcode(BaseModel):
    format: BarcodeFormat = BarcodeFormat.PDF417  # Required. Barcode format
    message: str  # Required. Message or payload to be displayed as a barcode
    messageEncoding: str = (
        "iso-8859-1"  # Required. Text encoding that is used to convert the message
    )
    altText: str = ""  # Optional. Text displayed near the barcode


class Location(BaseModel):
    latitude: float = 0.0  # Required. Latitude, in degrees, of the location
    longitude: float = 0.0  # Required. Longitude, in degrees, of the location
    altitude: float = 0  # Optional. Altitude, in meters, of the location
    distance: float = 0  # Optional. Maximum distance, in meters, from the location that the pass is relevant
    relevantText: str = ""  # Optional. Text displayed on the lock screen when the pass is currently relevant


class IBeacon(BaseModel):
    proximityUUID: (
        str  # Required. Unique identifier of a Bluetooth Low Energy location beacon
    )
    major: int  # Required. Major identifier of a Bluetooth Low Energy location beacon
    minor: int  # Required. Minor identifier of a Bluetooth Low Energy location beacon
    relevantText: str = ""  # Optional. Text displayed on the lock screen when the pass is currently relevant


class NFC(BaseModel):
    message: str  # Required. Message to be displayed on the lock screen when the pass is currently relevant
    encryptionPublicKey: (
        str  # Required. Public encryption key used by the Value Added Services protocol
    )
    requiresAuthentication: bool = False  # Optional. Indicates that the pass is not valid unless it contains a valid signature


class PassInformation(BaseModel):
    headerFields: typing.List[Field] = PydanticField(
        default_factory=list
    )  # Optional. Additional fields to be displayed in the header of the pass
    primaryFields: typing.List[Field] = PydanticField(
        default_factory=list
    )  # Optional. Fields to be displayed prominently in the pass
    secondaryFields: typing.List[Field] = PydanticField(
        default_factory=list
    )  # Optional. Fields to be displayed on the front of the pass
    backFields: typing.List[Field] = PydanticField(
        default_factory=list
    )  # Optional. Fields to be displayed on the back of the pass
    auxiliaryFields: typing.List[Field] = PydanticField(
        default_factory=list
    )  # Optional. Additional fields to be displayed on the front of the pass

    def addHeaderField(self, key, value, label, textAlignment=None):
        self.headerFields.append(
            Field(key=key, value=value, label=label, textAlignment=textAlignment)
        )

    def addPrimaryField(self, key, value, label, textAlignment=None):
        self.primaryFields.append(
            Field(key=key, value=value, label=label, textAlignment=textAlignment)
        )

    def addSecondaryField(self, key, value, label, textAlignment=None):
        self.secondaryFields.append(
            Field(key=key, value=value, label=label, textAlignment=textAlignment)
        )

    def addBackField(self, key, value, label, textAlignment=None):
        self.backFields.append(
            Field(key=key, value=value, label=label, textAlignment=textAlignment)
        )

    def addAuxiliaryField(self, key, value, label, textAlignment=None):
        self.auxiliaryFields.append(
            Field(key=key, value=value, label=label, textAlignment=textAlignment)
        )


# this registry identifies the different apple pass types by their name
pass_model_registry: Dict[str, PassInformation] = {}


def passmodel(name: str):
    """
    decorator function for registering a pass type
    """

    @functools.wraps(passmodel)
    def inner(cls):
        pass_model_registry[name] = cls
        cls._jsonname = name
        return cls

    return inner


@passmodel("boardingPass")
class BoardingPass(PassInformation):
    """
    see https://developer.apple.com/documentation/walletpasses/pass/boardingpass-data.dictionary
    """

    transitType: TransitType = TransitType.AIR


@passmodel("coupon")
class Coupon(PassInformation):
    """
    see https://developer.apple.com/documentation/walletpasses/pass/coupon-data.dictionary
    """


@passmodel("eventTicket")
class EventTicket(PassInformation):
    """
    see https://developer.apple.com/documentation/walletpasses/pass/eventticket-data.dictionary
    """


@passmodel("generic")
class Generic(PassInformation):
    """
    see https://developer.apple.com/documentation/walletpasses/pass/generic-data.dictionary
    """


@passmodel("storeCard")
class StoreCard(PassInformation):
    """
    see https://developer.apple.com/documentation/walletpasses/pass/storecard
    """


class Pass(BaseModel):
    # standard keys
    teamIdentifier: str
    """
    Required. Team identifier of the organization that originated and
    signed the pass, as issued by Apple.
    """
    passTypeIdentifier: str
    """
    Required. Pass type identifier, as issued by Apple. The value must
    correspond with your signing certificate. used for grouping."""
    organizationName: str
    """
    Required. Display name of the organization that originated and
    signed the pass."""
    serialNumber: str
    """Required. Serial number that uniquely identifies the pass.
    Must not be changed after creation"""
    description: str
    """Required. Brief description of the pass, used by the iOS accessibility technologies."""
    formatVersion: int = 1
    """Required. Version of the file format. The value must be 1."""

    # Visual Appearance Keys
    backgroundColor: str | None = None
    """Optional. Background color of the pass, specified as an CSS-style RGB triple. For example, rgb(23, 187, 82)."""
    foregroundColor: str | None = None
    """Optional. Foreground color of the pass, specified as a CSS-style RGB triple. For example, rgb(100, 10, 110)."""
    labelColor: str | None = None
    """Optional. Color of the label text, specified as a CSS-style RGB triple. For example, rgb(255, 255, 255)."""
    logoText: str | None = None
    """Optional. Text displayed next to the logo on the pass."""

    @computed_field  # type: ignore [no-redef]
    @deprecated("Use 'barcodes' instead")
    def barcode(self) -> Barcode | None:
        """
        deprecated, use barcodes instead.
        this field is implemented for backwards compatibility and returns the first barcode in the barcodes list.
        the setter overwrites the barcodes field
        """
        # return self.barcodes[0] if self.barcodes else None
        original_formats = legacy_barcode_formats
        legacyBarcode = self.barcodes[0] if self.barcodes else None
        if legacyBarcode is None:
            return None

        if legacyBarcode not in original_formats:
            legacyBarcode = Barcode(
                message=legacyBarcode.message,
                format=BarcodeFormat.PDF417,
                altText=legacyBarcode.altText,
            )

        return legacyBarcode

    @barcode.setter  # type: ignore [no-redef]
    @deprecated("Use 'barcodes' instead")
    def barcode(self, value: Barcode | None):
        self.barcodes = [value] if value is not None else None

    barcodes: list[Barcode] | None = None
    """Optional. Information specific to the pass’s barcode. The system uses the first valid"""
    suppressStripShine: bool = False
    """Optional. If true, the strip image is displayed."""

    # Web Service Keys
    webServiceURL: str | None = None
    """Optional. The URL of a web service that conforms to the API described in PassKit Web Service Reference.
    Must not be changed after creation"""
    authenticationToken: str | None = None
    """Optional. The authentication token to use with the web service.
    Minimum 16 chars
    Must not be changed after creation."""

    # Relevance Keys
    locations: list[Location] | None = None
    """Optional. Locations where the pass is relevant. For example, the location of your store."""
    ibeacons: list[IBeacon] | None = None
    """Optional. IBeacons data"""
    relevantDate: str | DateField | None = None
    """Optional. Date and time when the pass becomes relevant."""
    associatedStoreIdentifiers: list[str] | None = None
    """Optional. Identifies which merchants’ locations accept the pass."""

    appLaunchURL: str | None = None
    """Optional. A URL to be passed to the associated app when launching it."""
    userInfo: dict | None = None
    """Optional. Custom information for the pass."""
    expirationDate: str | DateField | None = None  # TODO: check if this is correct
    """Optional. Date and time when the pass expires."""
    voided: bool = False

    nfc: NFC | None = None
    """Optional. Information used for Value Added Service Protocol transactions."""

    @property
    def passInformation(self):
        """Returns the pass information object by checking all passmodel entries using all()"""
        return next(
            filter(
                lambda x: x is not None,
                (map(lambda x: getattr(self, x), pass_model_registry)),
            )
        )

    @classmethod
    def from_json(cls, json_str: str|bytes) -> "Pass":
        """
        validates a pass json string and returns a Pass object
        """
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            # in case of for example trailing commas, we use yaml
            # to parse the json string which swallows trailing commas
            # apple passes are allowed to have trailing commas, so we 
            # have to tolerate it too
            import yaml
            data = yaml.safe_load(json_str)
        return cls.model_validate(data)

class PkPass(BaseModel):
    """
    represents a PkPass file containing
    - a Pass object (results in pass.json)
    - all binary pass files (images)
    - manifest
    - signature (after signing)
    """

    pass_object: Pass | None = None

    files: dict = PydanticField(default_factory=dict, exclude=True)
    """# Holds the files to include in the .pkpass"""

    @classmethod
    def from_pass(cls, pass_object: Pass):
        return cls(pass_object=pass_object)

    @property
    def files_uuencoded(self) -> dict[str, str]:
        """
        Returns the files dict with the values uuencoded so that they can
        be stored in a JSON dict (e.g. for a REST API or a database)
        """
        return {k: bytearray_to_base64(v) for k, v in self.files.items()}

    @files_uuencoded.setter
    def files_uuencoded(self, files: dict[str, str]):
        """
        Loads the files from a dict that has been uuencoded
        """
        self.files = {k: base64_to_bytearray(v) for k, v in files.items()}

    @property
    def pass_dict(self) -> dict[str, Any]:
        return self.pass_object.model_dump(exclude_none=True, round_trip=True)

    @property
    def pass_json(self) -> str:
        return self.pass_object.model_dump_json(exclude_none=True, indent=4)

    def add_file(self, name: str, fd: typing.BinaryIO):
        """Adds a file to the pass. The file is stored in the files dict and the hash is stored in the hashes dict"""
        self.files[name] = fd.read()

    def files_from_json_dict(self, files: dict[str, str]):
        """
        Loads the files from a dict that has been uuencoded
        """
        self.files = {k: base64_to_bytearray(v) for k, v in files.items()}

    @property
    def manifest(self):
        return self.files.get("manifest.json")


    def create_manifest(self):
        """
        Creates the hashes for all the files included in the pass file.
        """
        excluded_files = ["signature", "manifest.json"]
        pass_json = self.pass_json

        # if there is a manifest we want to keep the order of the files
        old_manifest = self.manifest
        if old_manifest:
            old_manifest_json = json.loads(old_manifest, object_pairs_hook=OrderedDict)

        # renew pass.json
        self.files["pass.json"] = pass_json.encode("utf-8")
        hashes = {}
        for filename, filedata in sorted(self.files.items()):
            if filename not in excluded_files:
                hashes[filename] = hashlib.sha1(filedata).hexdigest()

        if old_manifest:
            # keep order of old manifest, remove unused files there and update new ones from hashes
            for filename in list(old_manifest_json.keys()):
                if filename not in hashes:
                    del old_manifest_json[filename]

            old_manifest_json.update(hashes)
            return json.dumps(old_manifest_json)
        return json.dumps(hashes)

    def sign(
        self,
        private_key_path: str | Path,
        certificate_path: str | Path,
        wwdr_certificate_path: str | Path,
    ):
        private_key, certificate, wwdr_certificate = crypto.load_key_files(
            private_key_path, certificate_path, wwdr_certificate_path
        )
        self.files["pass.json"] = self.pass_json.encode("utf-8")
 
        manifest = self.create_manifest()
        # manifest = self.files["manifest.json"].decode("utf-8")
        self.files["manifest.json"] = manifest.encode("utf-8")
        signature = crypto.sign_manifest(
            manifest,
            private_key,
            certificate,
            wwdr_certificate,
        )

        self.files["signature"] = signature
        # self.add_file("manifest.json", BytesIO(manifest.encode("utf-8")))
        # self.add_file("signature", BytesIO(signature))

    def build_zip(self, fh: typing.BinaryIO | None=None) -> zipfile.ZipFile:
        """
        builds a zip file from file content and returns the zipfile object
        if a file handle is given it writes the zip file to the file handle
        """
        if fh is None:
            fh = BytesIO()
        with zipfile.ZipFile(fh, "w") as zf:
            for filename, filedata in self.files.items():
                zf.writestr(filename, filedata)

            return zf
        
    def as_zip(self) -> BytesIO:
        """
        creates a zip file and gives it back as a BytesIO object
        """
        res = BytesIO()
        self.build_zip(res)
        return res

    def create(
        self,
        certificate: str,
        key: str,
        wwdr_certificate: str,
        password: Optional[bytes] = None,
        zip_file: typing.BinaryIO | BytesIO | None = None,
        sign: bool = True,
    ) -> typing.BinaryIO | BytesIO:
        """
        creates and signs the .pkpass file as a BytesIO object
        following the apple guidelines at https://developer.apple.com/documentation/walletpasses/building-a-pass#Sign-the-Pass-and-Create-the-Bundle
        """
        manifest = self.create_manifest()
        signature: Optional[bytes] = None
        if sign:
            signature = crypto.create_signature(
                manifest,
                key,
                certificate,
                wwdr_certificate,
                password,
            )
        if not zip_file:
            zip_file = BytesIO()
        self.create_zip(manifest, signature, zip_file=zip_file)
        return zip_file

    def create_zip(self, manifest, signature=None, zip_file=None):
        pass_json = self.pass_json
        with zipfile.ZipFile(zip_file or "pass.pkpass", "w") as zf:
            zf.writestr("pass.json", pass_json)
            zf.writestr("manifest.json", manifest)
            if signature:
                zf.writestr("signature", signature)
            for filename, filedata in self.files.items():
                zf.writestr(filename, filedata)

        return zip_file
    
    @classmethod
    def from_zip(cls, zip_file: typing.BinaryIO) -> "PkPass":
        """
        loads a .pkpass file from a zip file
        """
        with zipfile.ZipFile(zip_file) as zf:
            pass_json = zf.read("pass.json")
            # pass_dict = json.loads(pass_json)
            pass_object = Pass.from_json(pass_json)
            files = {name: zf.read(name) for name in zf.namelist()}
            res = cls.from_pass(pass_object)
            res.files = files

            return res


    @property
    def is_signed(self):
        return self.files.get("signature") is not None


    def verify(self, recompute_manifest=True):
        """
        verifies the signature of the pass
        :param: recompute_manifest: if True the manifest is recomputed before verifying
        """
        if not self.is_signed:
            raise ValueError("Pass is not signed")
        
        if recompute_manifest:
            manifest = self.create_manifest()
        else:
            manifest = self.manifest

        signature = self.files["signature"]

        return crypto.verify_manifest(manifest, signature)
    


# hack in an optional field for each passmodel(passtype) since these are not known at compile time
# because for each pass type the PassInformation is stored in a different field of which only one is used
for jsonname, klass in pass_model_registry.items():
    Pass.model_fields[jsonname] = FieldInfo(
        annotation=klass,
        required=False,
        default=None,
        exclude_none=True,  # type: ignore
    )

# add mutually exclusive validator so that only one variant can be defined
Pass.model_rebuild(force=True)
