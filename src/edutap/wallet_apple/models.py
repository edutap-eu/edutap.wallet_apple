from enum import Enum
from io import BytesIO
import os
from pathlib import Path

from typing import Any, Dict, Optional, Union
from typing_extensions import deprecated


from cryptography.x509 import load_pem_x509_certificate, load_der_x509_certificate
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.hazmat.primitives.serialization.pkcs7 import (
    PKCS7SignatureBuilder, PKCS7Options
)

from pydantic import BaseModel
from pydantic import computed_field
from pydantic import Field as PydanticField
from pydantic.fields import FieldInfo


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


legacy_barcode_formats = [BarcodeFormat.PDF417, BarcodeFormat.QR, BarcodeFormat.AZTEC]
"""Barcode formats that are supported by iOS 6 and 7"""


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
    changeMessage: str = (
        ""  # Optional. Format string for the alert text that is displayed when the pass is updated
    )
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
    distance: float = (
        0  # Optional. Maximum distance, in meters, from the location that the pass is relevant
    )
    relevantText: str = (
        ""  # Optional. Text displayed on the lock screen when the pass is currently relevant
    )


class IBeacon(BaseModel):
    proximityUUID: (
        str  # Required. Unique identifier of a Bluetooth Low Energy location beacon
    )
    major: int  # Required. Major identifier of a Bluetooth Low Energy location beacon
    minor: int  # Required. Minor identifier of a Bluetooth Low Energy location beacon
    relevantText: str = (
        ""  # Optional. Text displayed on the lock screen when the pass is currently relevant
    )


class NFC(BaseModel):
    message: str  # Required. Message to be displayed on the lock screen when the pass is currently relevant
    encryptionPublicKey: (
        str  # Required. Public encryption key used by the Value Added Services protocol
    )
    requiresAuthentication: bool = (
        False  # Optional. Indicates that the pass is not valid unless it contains a valid signature
    )


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


pass_model_registry: Dict[str, PassInformation] = {}
"""
this registry identifies the different apple pass types by their name
"""


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
    files: dict = PydanticField(default_factory=dict, exclude=True)
    """# Holds the files to include in the .pkpass"""
    hashes: dict = PydanticField(default_factory=dict, exclude=True)
    """# Holds the hashes to include in the .pkpass as manifest.json"""

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
    def pass_dict(self):
        return self.model_dump(exclude_none=True, round_trip=True)

    @property
    def pass_json(self):
        return self.model_dump_json(exclude_none=True, indent=4)

    @property
    def passInformation(self):
        """Returns the pass information object by checkinf all passmodel entries using all()"""
        return next(
            filter(
                lambda x: x is not None,
                (map(lambda x: getattr(self, x), pass_model_registry)),
            )
        )

    def addFile(self, name: str, fd: typing.BinaryIO):
        """Adds a file to the pass. The file is stored in the files dict and the hash is stored in the hashes dict"""
        self.files[name] = fd.read()

    def files_from_json_dict(self, files: dict[str, str]):
        """
        Loads the files from a dict that has been uuencoded
        """
        self.files = {k: base64_to_bytearray(v) for k, v in files.items()}

    def _createManifest(self):
        """
        Creates the hashes for all the files included in the pass file.
        """
        pass_json = self.pass_json
        self.hashes["pass.json"] = hashlib.sha1(pass_json.encode("utf-8")).hexdigest()
        for filename, filedata in self.files.items():
            self.hashes[filename] = hashlib.sha1(filedata).hexdigest()
        return json.dumps(self.hashes)

    def create(
        self,
        certificate: str,
        key: str,
        wwdr_certificate: str,
        password: Optional[str] = None,
        zip_file: typing.BinaryIO | BytesIO | None = None,
        sign: bool = True,
    ) -> typing.BinaryIO | BytesIO:
        """
        creates and signs the .pkpass file as a BytesIO object

        following the apple guidlines at https://developer.apple.com/documentation/walletpasses/building-a-pass#Sign-the-Pass-and-Create-the-Bundle

        """
        manifest = self._createManifest()
        signature = None
        if sign:
            signature: bytes = self._createSignature(
                manifest,
                certificate,
                key,
                wwdr_certificate,
                password,
            )
        if not zip_file:
            zip_file = BytesIO()
        self._createZip(manifest, signature, zip_file=zip_file)
        return zip_file

    def _sign_manifest(
        self,
        manifest: str,
        certificate_path: Union[str, Path],
        private_key_path: Union[str, Path],
        wwdr_certificate_path: Union[str, Path],
        password: Optional[bytes],
    ) -> bytes:
        """
        :param manifest: contains the manifest content as json string
        :param certificate: path to certificate
        :param key: path to private key
        :wwdr_certificate: path to wwdr_certificate
        :return: signature as bytes
        """

        # PKCS7: see https://www.youtube.com/watch?v=3YJ0by1r3qE
        with open(certificate_path, "rb") as fh:
            certificate_data = fh.read()
        with open(private_key_path, "rb") as fh:
            private_key_data = fh.read()
        with open(wwdr_certificate_path, "rb") as fh:
            wwdr_certificate_data = fh.read()

        certificate = load_pem_x509_certificate(certificate_data, default_backend())
        private_key = load_pem_private_key(
            private_key_data, password=password, backend=default_backend()
        )
        # if not isinstance(private_key, (RSAPrivateKey, EllipticCurvePrivateKey)):
        #     raise TypeError("Private key must be an RSAPrivateKey or EllipticCurvePrivateKey")
        wwdr_certificate = load_pem_x509_certificate(
            wwdr_certificate_data, default_backend()
        )

        signature_builder = (
            PKCS7SignatureBuilder()
            .set_data(manifest.encode("utf-8"))
            .add_signer(certificate, private_key, hashes.SHA256())
            .add_certificate(wwdr_certificate)
        )

        pkcs7_signature = signature_builder.sign(Encoding.DER, [])
        return pkcs7_signature

    def _createSignature(
        self,
        manifest,
        certificate_path: Union[str, Path],
        private_key_path: Union[str, Path],
        wwdr_certificate_path: Union[str, Path],
        password: Optional[bytes] = None,
    ) -> bytes:
        """
        Creates the signature for the pass file.
        """

        # check for cert file existence
        if not os.path.exists(private_key_path):
            raise FileNotFoundError(f"Key file {private_key_path} not found")
        if not os.path.exists(certificate_path):
            raise FileNotFoundError(f"Certificate file {certificate_path} not found")
        if not os.path.exists(wwdr_certificate_path):
            raise FileNotFoundError(
                f"WWDR Certificate file {wwdr_certificate_path} not found"
            )

        pk7 = self._sign_manifest(
            manifest,
            certificate_path,
            private_key_path,
            wwdr_certificate_path,
            password,
        )

        return pk7

    def _createZip(self, manifest, signature=None, zip_file=None):
        pass_json = self.pass_json
        zf = zipfile.ZipFile(zip_file or "pass.pkpass", "w")
        zf.writestr("pass.json", pass_json)
        zf.writestr("manifest.json", manifest)
        if signature:
            zf.writestr("signature", signature)
        for filename, filedata in self.files.items():
            zf.writestr(filename, filedata)
        zf.close()

    def _verify_manifest(self, manifest, signature, cert_pem=None):
        """
        Verifies the manifest against the signature.
        Currently no check against the cert supported, only the
        manifest is verified against the signature to check for manipulation
        in the manifest
        """
        from cryptography.hazmat.bindings._rust import test_support # this is preliminary hence the local import

        # if cert_pem:
        #     with  open(cert_pem, "rb") as fh:
        #         cert = load_pem_x509_certificate(fh.read(), default_backend())
        # else:
        #     cert = None

        test_support.pkcs7_verify(
            Encoding.DER,
            signature,
            manifest.encode("utf-8"),
            [], #
            [PKCS7Options.NoVerify],
        )


# hack in an optional field for each passmodel(passtype) since these are not known at compile time
# because for each pass type the PassInformation is stored in a different field of which only one is used
for jsonname, cls in pass_model_registry.items():
    Pass.model_fields[jsonname] = FieldInfo(
        annotation=cls, required=False, default=None, exclude_none=True
    )

# add mutually exclusive valdator so that only one variant can be defined
Pass.model_rebuild(force=True)
