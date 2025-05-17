from collections import OrderedDict
from edutap.wallet_apple import crypto
from edutap.wallet_apple.models.datatypes import *
from edutap.wallet_apple.models.enums import *
from edutap.wallet_apple.models.semantic_tags import *
from io import BytesIO
from pathlib import Path
from pydantic import AnyHttpUrl
from pydantic import AnyUrl
from pydantic import BaseModel
from pydantic import computed_field
from pydantic import EmailStr
from pydantic import Field as PydanticField
from pydantic import model_serializer
from pydantic import SerializationInfo
from pydantic.fields import FieldInfo
from typing import Any
from typing import Dict
from typing_extensions import deprecated

import base64
import functools
import hashlib
import json
import typing
import yaml
import zipfile


def bytearray_to_base64(bytearr):
    encoded_data = base64.b64encode(bytearr)
    return encoded_data.decode("utf-8")


def base64_to_bytearray(base64_str):
    decoded_data = base64.b64decode(base64_str)
    return decoded_data


# Barcode formats that are supported by iOS 6 and 7
legacy_barcode_formats = [BarcodeFormat.PDF417, BarcodeFormat.QR, BarcodeFormat.AZTEC]


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
    altitude: float | None = None  # Optional. Altitude, in meters, of the location
    distance: float = (
        0  # Optional. Maximum distance, in meters, from the location that the pass is relevant
    )
    relevantText: str = (
        ""  # Optional. Text displayed on the lock screen when the pass is currently relevant
    )


IBeacon = Beacon  # Alias for backward compatibility


class NFC(BaseModel):
    message: str  # Required. Message to be displayed on the lock screen when the pass is currently relevant
    encryptionPublicKey: (
        str  # Required. Public encryption key used by the Value Added Services protocol
    )
    requiresAuthentication: bool = (
        False  # Optional. Indicates that the pass is not valid unless it contains a valid signature
    )


class PassInformation(BaseModel):
    class Config:
        extra = "allow"  # Erlaubt zusätzliche Felder

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

    additionalInfoFields: typing.List[Field] = PydanticField(
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
        cls.jsonname = name
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
    """
    Represents a pass object. This is the base class for all pass types.

    see: https://developer.apple.com/documentation/walletpasses/pass
    """

    # Attribute order as in Apple's documentation to make future changes easier!
    # last checked: 2025-05-16

    class Config:
        extra = "allow"  # Erlaubt zusätzliche Felder

    # standard keys
    accessibilityURL: str | None = None
    """
    Optional.
    A URL that links to your accessiblity content, or the venue’s.
    This key works only for poster event tickets.
    """

    addOnURL: AnyUrl | None = None
    """
    Optional.
    A URL that can link to experiences that someone can add to the pass.
    This key works only for poster event tickets.
    """

    appLaunchURL: AnyUrl | None = None
    """
    Optional.
    A URL the system passes to the associated app from associatedStoreIdentifiers during launch.
    The app receives this URL in the application(_:didFinishLaunchingWithOptions:) and application(_:open:options:) methods of its app delegate.
    This key isn’t supported for watchOS.
    """

    associatedStoreIdentifiers: list[str] | None = None  # [number]
    """
    Optional.
    An array of App Store identifiers for apps associated with the pass. The associated app on a device is the first item in the array that’s compatible with that device.
    A link to launch the app is on the back of the pass. If the app isn’t installed, the link opens the App Store.
    This key works only for payment passes.
    This key isn’t supported for watchOS.
    """

    auxiliaryStoreIdentifiers: list[str] | None = None  # [number]
    """
    Optional.
    An array of additional App Store identifiers for apps associated with the pass. The associated app on a device is the first item in the array that’s compatible with that device.
    This key works only for poster event tickets. A link to launch the app is in the event guide of the pass. If the app isn’t installed, the link opens the App Store.
    This key isn’t supported for watchOS.
    """

    authenticationToken: bytes | None = None
    """
    Optional. The authentication token to use with the web service in the webServiceURL key.
    Minimum 16 chars
    Must not be changed after creation.
    """

    backgroundColor: str | None = None
    """
    Optional.
    A background color for the pass, specified as a CSS-style RGB triple, such as rgb(23, 187, 82).
    """

    bagPolicyURL: AnyUrl | None = None
    """
    Optional.
    A URL that links to the bag policy of the venue for the event that the pass represents.
    This key works only for poster event tickets.
    """

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
    """
    Optional.
    An array of objects that represent possible barcodes on a pass.
    The system uses the first displayable barcode for the device.
    """

    beacons: list[Beacon] | None = None

    # boardingPass: BoardingPass | None = None
    """
    Optional.
    An object that contains the information for a boarding pass
    """

    contactVenueEmail: EmailStr | None = None
    """
    Optional.
    The preferred email address to contact the venue, event, or issuer.
    This key works only for poster event tickets.
    """

    contactVenuePhoneNumber: str | None = None
    """
    Optional.
    The phone number for contacting the venue, event, or issuer.
    This key works only for poster event tickets.
    """

    contactVenueWebsite: AnyHttpUrl | None = None
    """
    Optional.
    A URL that links to the website of the venue, event, or issuer.
    This key works only for poster event tickets.
    """

    # coupon: Coupon | None = None
    """
    Optional.
    An object that contains the information for a coupon.
    """

    description: str
    """
    Required.
    A short description that iOS accessibility technologies use for a pass.
    """

    directionsInformationURL: AnyUrl | None = None
    """
    Optional.
    A URL that links to directions for the event.

    This key works only for poster event tickets.
    """

    eventLogoText: str | None = None
    """
    Optional.
    The text to display next to the logo on the pass.
    This key works only for poster event tickets
    """

    # eventTicket = EventTicket | None = None
    """
    Optional.
    An object that contains the information for an event ticket.
    """

    expirationDate: str | DateField | None = None
    """
    Optional.
    The date and time the pass expires.
    The value needs to be a complete date that includes hours and minutes, and may optionally include seconds.
    """

    footerBackgroundColor: str | None = None
    """
    Optional.
    A background color for the footer of the pass, specified as a CSS-style RGB triple, such as rgb(100, 10, 110).
    This key works only for poster event tickets.
    """

    foregroundColor: str | None = None
    """
    Optional.
    A foreground color for the pass, specified as a CSS-style RGB triple, such as rgb(100, 10, 110).
    """

    formatVersion: int = 1
    """
    Required.
    The version of the file format. The value needs to be 1.
    """

    # generic: Generic | None = None
    """
    Optional.
    An object that contains the information for a generic pass.
    """

    groupingIdentifier: str | None = None
    """
    Optional.
    An identifier the system uses to group related boarding passes or event tickets.
    Wallet displays passes with the same groupingIdentifier, passTypeIdentifier, and type as a group.
    Use this identifier to group passes that are tightly related, such as boarding passes for different connections on the same trip.
    """

    labelColor: str | None = None
    """
    Optional.
    A color for the label text of the pass, specified as a CSS-style RGB triple, such as rgb(100, 10, 110).
    If you don’t provide a value, the system determines the label color.
    """

    locations: list[Location] | None = None
    # Field(
    #     default=None,
    #     # max_length=10,
    # )
    """
    Optional.
    An array of up to 10 objects that represent geographic locations the system uses to show a relevant pass.
    """

    logoText: str | None = None
    """
    Optional.
    The text to display next to the logo on the pass.
    This key doesn’t work for poster event tickets.
    """

    maxDistance: int | None = None
    """
    Optional.
    The maximum distance, in meters, from a location in the locations array at which the pass is relevant.
    The system uses the smaller of this distance or the default distance.
    """

    merchandiseURL: AnyUrl | None = None
    """
    Optional.
    A URL that links to a site for ordering merchandise for the event that the pass represents.
    This key works only for poster event tickets.
    """

    nfc: NFC | None = None
    """
    Optional.
    An object that contains the information to use for Value-Added Services protocol transactions.
    """

    orderFoodURL: AnyUrl | None = None
    """
    Optional.
    A URL that links to the food ordering page for the event that the pass represents.
    This key works only for poster event tickets.
    """

    organizationName: str
    """
    Required. Display name of the organization that originated and
    signed the pass."""

    parkingInformationURL: AnyUrl | None = None
    """
    Optional.
    A URL that links to parking information for the event that the pass represents.
    This key works only for poster event tickets.
    """

    passTypeIdentifier: str
    """
    Required.
    The pass type identifier that’s registered with Apple.
    The value needs to be the same as the distribution certificate that signs the pass.
    """

    preferredStyleSchemes: list[Literal["posterEventTicker", "eventTicket"]] | None = None
    """
    Optional.
    An array of schemes to validate the pass with. The system validates the pass and its contents to ensure they meet the schemes’ requirements, falling back to the designed type if validation fails for all the provided schemes.
    """

    purchaseParkingURL: AnyUrl | None = None
    """
    Optional.
    A URL that links to a site to purchase parking for the event that the pass represents.
    This key works only for poster event tickets.
    """

    relevantDate: str | DateField | None = None  # Deprecated: use relevantDates instead
    """
    Optional.
    The date and time when the pass becomes relevant, as a W3C timestamp, such as the start time of a movie. The value needs to be a complete date that includes hours and minutes, and may optionally include seconds.
    For information about the W3C timestamp format, see Time and Date Formats on the W3C website.
    This object is deprecated. Use relevantDates instead.
    """

    relevantDates: list[DateField] | None = None
    """
    Optional.
    An array of objects that represent date intervals that the system uses to show a relevant pass.
    """

    sellURL: AnyUrl | None = None
    """
    Optional.
    A URL that links to the selling flow for the ticket the pass represents.
    This key works only for poster event tickets.
    """

    semantics: dict[str, Any] | None = None
    """
    Optional.
    An object that contains machine-readable metadata the system uses to offer a pass and suggest related actions.
    For example, setting Don’t Disturb mode for the duration of a movie.
    """

    serialNumber: str
    """
    Required.
    An alphanumeric serial number.
    The combination of the serial number and pass type identifier needs to be unique for each pass.
    """

    sharingProhibited: bool = False
    """
    Optional.
    A Boolean value introduced in iOS 11 that controls whether to show the Share button on the back of a pass.
    A value of true removes the button. The default value is false.
    This flag has no effect in earlier versions of iOS, nor does it prevent sharing the pass in some other way.
    """

    # storeCard: StoreCard | None = None
    """
    Optional.
    An object that contains the information for a store card.
    """

    suppressStripShine: bool = True
    """
    Optional.
    A Boolean value that controls whether to display the strip image without a shine effect.
    The default value is true.
    """

    suppressHeaderDarkening: bool = False
    """
    Optional.
    A Boolean value that controls whether to display the header darkening gradient on poster event tickets.
    The default value is false.
    """

    teamIdentifier: str
    """
    Required.
    The Team ID for the Apple Developer Program account that registered the pass type identifier.
    """

    transferURL: AnyUrl | None = None
    """
    Optional.
    A URL that links to the transferring flow for the ticket that the pass represents.
    This key works only for poster event tickets.
    """

    transitInformationURL: AnyUrl | None = None
    """
    Optional.
    A URL that links to information about transit options in the area of the event that the pass represents.
    This key works only for poster event tickets.
    """

    useAutomaticColors: bool | None = None
    """
    Optional.
    A Boolean value that controls whether Wallet computes the foreground and label color that the pass uses. The system derives the background color from the background image of the pass.
    This key works only for poster event tickets.
    This key ignores the values that foregroundColor and labelColor specify.
    """

    userInfo: dict | None = None
    """
    Optional.
    A JSON dictionary that contains any custom information for companion apps.
    The data doesn’t appear to the user.
    For example, a pass for a cafe might include information about the customer’s favorite drink and sandwich in a machine-readable form.
    The companion app uses the data for placing an order for the usual.
    """

    voided: bool = False
    """
    Optional.
    A Boolean value that indicates that the pass is void, such as a redeemed, one-time-use coupon.
    The default value is false.
    """

    webServiceURL: str | None = None
    """
    Optional.
    The URL for a web service that you use to update or personalize the pass.
    The URL can include an optional port number.
    """

    # experimental/reverse engineered, can be extracted from boarding pass
    isShellPass: bool = False

    # experimental/reverse engineered
    revoked: bool = False

    @property
    def pass_information(self):
        """Returns the pass information object by checking all passmodel entries using all()"""
        return next(
            filter(
                lambda x: x is not None,
                (map(lambda x: getattr(self, x), pass_model_registry)),
            )
        )

    @classmethod
    def from_json(cls, json_str: str | bytes) -> "Pass":
        """
        validates a pass json string and returns a Pass object
        """
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            # in case of for example trailing commas, we use yaml
            # to parse the json string which swallows trailing commas
            # apple passes are allowed to have trailing commas, so we
            # have to tolerate it too
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

    @property
    def pass_object_safe(self):
        if self.pass_object is None:
            raise ValueError("Pass object is not set")
        return self.pass_object

    files: dict = PydanticField(default_factory=dict, exclude=True)
    """# Holds the files to include in the .pkpass"""

    @classmethod
    def from_pass(cls, pass_object: Pass):
        return cls(pass_object=pass_object)

    @property
    def is_signed(self):
        return self.files.get("signature") is not None

    class Config:
        """
        Configuration for PkPass model.
        """

        arbitrary_types_allowed = True
        # necessary for the model_serializer can have return type other than str|dict
        # TODO: check if this is correct

    @model_serializer
    def dump(
        self, info: SerializationInfo
    ) -> dict[str, Any] | zipfile.ZipFile | BytesIO | str:
        """
        dumps the pass to a zip file or a dict

        this function is work in progress since there is a strange behavior
        in pydantic concerning serialization of file objects:
        https://github.com/pydantic/pydantic/issues/8907#issuecomment-2550673061.

        When it is fixed, it will work like:
        ```pkpass.model_dump(mode="BytesIO")```
        currently it returns a SerializationIterator object which is not what we want

        what already works is:
        ```pkpass.model_dump(mode="zip")``` which returns a zipfile.ZipFile object

        """
        res: Any
        if info.mode == "zip":
            res = self._build_zip()
        elif info.mode == "python":
            res = self.pass_object.model_dump() if self.pass_object else {}
        elif info.mode == "json":
            res = (
                self.pass_object.model_dump_json(exclude_none=True, indent=4)
                if self.pass_object
                else {}
            )
        elif info.mode == "BytesIO":
            res = self.as_zip_bytesio()
        else:
            raise ValueError(f"Unsupported mode {info.mode}")

        return res

    def as_zip_bytesio(self) -> BytesIO:
        """
        creates a zip file and gives it back as a BytesIO object
        """
        res = BytesIO()
        self._build_zip(res)
        res.seek(0)
        return res

    @property
    def _pass_dict(self) -> dict[str, Any]:
        if self.pass_object is None:
            raise ValueError("Pass object is not set")
        return self.pass_object.model_dump(exclude_none=True, round_trip=True)

    @property
    def _pass_json(self) -> str:
        if self.pass_object is None:
            raise ValueError("Pass object is not set")
        return self.pass_object.model_dump_json(exclude_none=True, indent=4)

    def _add_file(self, name: str, fd: typing.BinaryIO):
        """Adds a file to the pass. The file is stored in the files dict and the hash is stored in the hashes dict"""
        self.files[name] = fd.read()

    @property
    def _manifest(self):
        return self.files.get("manifest.json")

    def _create_manifest(self):
        """
        Creates the hashes for all the files included in the pass file.
        """
        excluded_files = ["signature", "manifest.json"]
        pass_json = self._pass_json

        # if there is a manifest we want to keep the order of the files
        old_manifest = self._manifest
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
        self.files["pass.json"] = self._pass_json.encode("utf-8")

        manifest = self._create_manifest()
        # manifest = self.files["manifest.json"].decode("utf-8")
        self.files["manifest.json"] = manifest.encode("utf-8")
        signature = crypto.sign_manifest(
            manifest,
            private_key,
            certificate,
            wwdr_certificate,
        )

        self.files["signature"] = signature

    def _build_zip(self, fh: typing.BinaryIO | None = None) -> zipfile.ZipFile:
        """
        builds a zip file from file content and returns the zipfile object
        if a file handle is given it writes the zip file to the file handle
        """
        if fh is None:
            fh = BytesIO()

        if "pass.json" not in self.files:
            self.files["pass.json"] = self._pass_json.encode("utf-8")
        with zipfile.ZipFile(fh, "w") as zf:
            for filename, filedata in self.files.items():
                zf.writestr(filename, filedata)

            zf.close()
            return zf

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

    def verify(self, recompute_manifest=True):
        """
        verifies the signature of the pass
        :param: recompute_manifest: if True the manifest is recomputed before verifying
        """
        if not self.is_signed:
            raise ValueError("Pass is not signed")

        if recompute_manifest:
            manifest = self._create_manifest()
        else:
            manifest = self._manifest

        signature = self.files["signature"]

        return crypto.verify_manifest(manifest, signature)


# hack in an optional field for each passmodel(passtype) since these are not known at compile time
# because for each pass type the PassInformation is stored in a different field of which only one is used
for jsonname, klass in pass_model_registry.items():
    Pass.model_fields[jsonname] = FieldInfo(  # type: ignore
        annotation=klass,  # type: ignore
        required=False,
        default=None,
        exclude_none=True,
    )
# add mutually exclusive validator so that only one variant can be defined
Pass.model_rebuild(force=True)
