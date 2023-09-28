from enum import Enum
import functools
import hashlib
from io import BytesIO
import json
from numbers import Number
import typing
import zipfile

from pydantic import BaseModel, Field as PydanticField, computed_field
from pydantic.fields import FieldInfo

from M2Crypto import SMIME, X509
from M2Crypto.X509 import X509_Stack
                          

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


class MyEnum(Enum):
    def __str__(self):
        return self.value
    
    a=1
    b=2
    
class Schas(BaseModel):
    i: int =1
    s: str = "xx"
    
class Field(BaseModel):
    key: str  # Required. The key must be unique within the scope
    value: str | int | float  # Required. Value of the field. For example, 42
    label: str = ""  # Optional. Label text for the field.
    changeMessage: str = ""  # Optional. Format string for the alert text that is displayed when the pass is updated
    # textAlignment: Alignment = Alignment.LEFT
    # textAlignment: Alignment|None = None # Optional. Alignment for the field’s contents
    textAlignment: MyEnum | None = None  # Optional. Alignment for the field’s contents


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
    proximityUUID: str  # Required. Unique identifier of a Bluetooth Low Energy location beacon
    major: int  # Required. Major identifier of a Bluetooth Low Energy location beacon
    minor: int  # Required. Minor identifier of a Bluetooth Low Energy location beacon
    relevantText: str = ""  # Optional. Text displayed on the lock screen when the pass is currently relevant


class NFC(BaseModel):
    message: str  # Required. Message to be displayed on the lock screen when the pass is currently relevant
    encryptionPublicKey: str  # Required. Public encryption key used by the Value Added Services protocol


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

    def addHeaderField(self, key, value, label):
        self.headerFields.append(Field(key=key, value=value, label=label))

    def addPrimaryField(self, key, value, label):
        self.primaryFields.append(Field(key=key, value=value, label=label))

    def addSecondaryField(self, key, value, label):
        self.secondaryFields.append(Field(key=key, value=value, label=label))

    def addBackField(self, key, value, label):
        self.backFields.append(Field(key=key, value=value, label=label))

    def addAuxiliaryField(self, key, value, label):
        self.auxiliaryFields.append(Field(key=key, value=value, label=label))


pass_model_registry = {}


def passmodel(name: str):
    @functools.wraps(passmodel)
    def inner(cls):
        pass_model_registry[name] = cls
        cls._jsonname = name
        return cls

    return inner


@passmodel("boardingPass")
class BoardingPass(PassInformation):
    transitType: TransitType = TransitType.AIR


@passmodel("coupon")
class Coupon(PassInformation):
    pass


@passmodel("eventTicket")
class EventTicket(PassInformation):
    pass


@passmodel("generic")
class Generic(PassInformation):
    pass


@passmodel("storeCard")
class StoreCard(PassInformation):
    pass



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
    """Required. Serial number that uniquely identifies the pass."""
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
    # barcode: Barcode | None = PydanticField(
    #     default=None, deprecated=True, description="Use barcodes instead"
    # )
    @computed_field
    @property
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
            legacyBarcode = Barcode(message=legacyBarcode.message, format=BarcodeFormat.PDF417, altText=legacyBarcode.altText)
            
        return legacyBarcode

    
    
    @barcode.setter
    def barcode(self, value: Barcode | None):
        self.barcodes = [value] if value is not None else None
    
    barcodes: list[Barcode] | None = None
    """Optional. Information specific to the pass’s barcode. The system uses the first valid"""
    suppressStripShine: bool = False
    """Optional. If true, the strip image is displayed."""

    # Web Service Keys
    webServiceURL: str | None = None
    """Optional. The URL of a web service that conforms to the API described in PassKit Web Service Reference."""
    authenticationToken: str | None = None
    """Optional. The authentication token to use with the web service."""

    # Relevance Keys
    locations: list[Location] | None = None
    """Optional. Locations where the pass is relevant. For example, the location of your store."""
    ibeacons: list[IBeacon] | None = None
    """Optional. IBeacons data"""
    relevantDate: DateField | str | None = None
    """Optional. Date and time when the pass becomes relevant."""
    associatedStoreIdentifiers: list[str] | None = None
    """Optional. Identifies which merchants’ locations accept the pass."""

    appLaunchURL: str | None = None
    """Optional. A URL to be passed to the associated app when launching it."""
    userInfo: dict | None = None
    """Optional. Custom information for the pass."""
    expirationDate: DateField | None = None  # TODO: check if this is correct
    """Optional. Date and time when the pass expires."""
    voided: bool = False

    nfc: NFC | None = None
    """Optional. Information used for Value Added Service Protocol transactions."""

    @property
    def pass_dict(self):
        return self.model_dump(exclude_none=True)
    
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
        password: str,
        zip_file: typing.BinaryIO | None = None,
    ):
        manifest = self._createManifest()
        signature = self._createSignature(
            manifest, certificate, key, wwdr_certificate, password
        )
        if not zip_file:
            zip_file = BytesIO()
        self._createZip(manifest, signature, zip_file=zip_file)
        return zip_file

    def create_pass_object(self, passtype: str):
        passcls = pass_model_registry[passtype]
        setattr(self, passtype, passcls())


    def _get_smime(self, certificate, key, wwdr_certificate, password):
        """
        :return: M2Crypto.SMIME.SMIME
        """
        # from M2Crypto.X509 import X509_Stack
        def passwordCallback(*args, **kwds):
            return bytes(password, encoding='ascii')

        smime = SMIME.SMIME()

        wwdrcert = X509.load_cert(wwdr_certificate)
        stack = X509_Stack()
        stack.push(wwdrcert)
        smime.set_x509_stack(stack)

        smime.load_key(key, certfile=certificate, callback=passwordCallback)
        return smime

    def _sign_manifest(self, manifest, certificate, key, wwdr_certificate, password) -> SMIME.PKCS7:
        """
        :return: M2Crypto.SMIME.PKCS7
        """
        smime = self._get_smime(certificate, key, wwdr_certificate, password)
        pkcs7 = smime.sign(
            SMIME.BIO.MemoryBuffer(bytes(manifest, encoding='utf8')),
            flags=SMIME.PKCS7_DETACHED | SMIME.PKCS7_BINARY
        )
        return pkcs7
    
    def _createSignature(
        self, manifest, certificate, key, wwdr_certificate, password
    ):
        """
        Creates the signature for the pass file.
        """
        pk7 = self._sign_manifest(manifest, certificate, key, wwdr_certificate, password)
        der = SMIME.BIO.MemoryBuffer()
        pk7.write_der(der)
        return der.read()
    
    def _createZip(self, manifest, signature, zip_file=None):
        pass_json = self.pass_json
        zf = zipfile.ZipFile(zip_file or 'pass.pkpass', 'w')
        zf.writestr('signature', signature)
        zf.writestr('manifest.json', manifest)
        zf.writestr('pass.json', pass_json)
        for filename, filedata in self.files.items():
            zf.writestr(filename, filedata)
        zf.close()

    
# hack in an optional field for each passmodel(passtype) since these are not known at compile time
# because for each pass type whe PassInformation is stored in a different field of which only one is used
for jsonname, cls in pass_model_registry.items():
    Pass.model_fields[jsonname] = FieldInfo(
        annotation=cls, required=False, default=None, exclude_none=True
    )

# add mutually exclusive valdator so that only one variant can be defined
Pass.model_rebuild(force=True)
