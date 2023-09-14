from enum import Enum
from numbers import Number
import typing

from pydantic import BaseModel, Field as PydanticField
from pydantic.fields import FieldInfo


class Alignment(Enum):
    LEFT = 'PKTextAlignmentLeft'
    CENTER = 'PKTextAlignmentCenter'
    RIGHT = 'PKTextAlignmentRight'
    JUSTIFIED = 'PKTextAlignmentJustified'
    NATURAL = 'PKTextAlignmentNatural'


class BarcodeFormat(Enum):
    PDF417 = 'PKBarcodeFormatPDF417'
    QR = 'PKBarcodeFormatQR'
    AZTEC = 'PKBarcodeFormatAztec'
    CODE128 = 'PKBarcodeFormatCode128'


class TransitType(Enum):
    AIR = 'PKTransitTypeAir'
    TRAIN = 'PKTransitTypeTrain'
    BUS = 'PKTransitTypeBus'
    BOAT = 'PKTransitTypeBoat'
    GENERIC = 'PKTransitTypeGeneric'


class DateStyle(Enum):
    NONE = 'PKDateStyleNone'
    SHORT = 'PKDateStyleShort'
    MEDIUM = 'PKDateStyleMedium'
    LONG = 'PKDateStyleLong'
    FULL = 'PKDateStyleFull'


class NumberStyle(Enum):
    DECIMAL = 'PKNumberStyleDecimal'
    PERCENT = 'PKNumberStylePercent'
    SCIENTIFIC = 'PKNumberStyleScientific'
    SPELLOUT = 'PKNumberStyleSpellOut'


class Field(BaseModel):
    
    key: str  # Required. The key must be unique within the scope
    value: str | int | float  # Required. Value of the field. For example, 42
    label: str = ''  # Optional. Label text for the field.
    changeMessage: str = ''  # Optional. Format string for the alert text that is displayed when the pass is updated
    textAlignment: Alignment = Alignment.LEFT


class DateField(Field):
    dateStyle: DateStyle = DateStyle.SHORT
    timeStyle: DateStyle = DateStyle.SHORT
    isRelative: bool = False
    ignoresTimeZone: bool = False
    

class NumberField(Field):
    numberStyle: NumberStyle = NumberStyle.DECIMAL
    
    
class CurrencyField(Field):
    currencyCode: str = 'USD'


class Barcode(BaseModel):
    format: BarcodeFormat = BarcodeFormat.PDF417  # Required. Barcode format
    message: str  # Required. Message or payload to be displayed as a barcode
    messageEncoding: str = 'iso-8859-1'  # Required. Text encoding that is used to convert the message
    altText: str = ''  # Optional. Text displayed near the barcode
    
    
class Location(BaseModel):
    latitude: float = 0.0 # Required. Latitude, in degrees, of the location
    longitude: float = 0.0 # Required. Longitude, in degrees, of the location
    altitude: float = 0  # Optional. Altitude, in meters, of the location
    distance: float = 0  # Optional. Maximum distance, in meters, from the location that the pass is relevant
    relevantText: str = ''  # Optional. Text displayed on the lock screen when the pass is currently relevant
    
    
class IBeacon(BaseModel):
    proximityUUID: str  # Required. Unique identifier of a Bluetooth Low Energy location beacon
    major: int  # Required. Major identifier of a Bluetooth Low Energy location beacon
    minor: int  # Required. Minor identifier of a Bluetooth Low Energy location beacon
    relevantText: str = ''  # Optional. Text displayed on the lock screen when the pass is currently relevant
    
    
class PassInformation(BaseModel):
    headerFields: typing.List[Field] = PydanticField(default_factory=list)  # Optional. Additional fields to be displayed in the header of the pass
    primaryFields: typing.List[Field] = PydanticField(default_factory=list)  # Optional. Fields to be displayed prominently in the pass
    secondaryFields: typing.List[Field] = PydanticField(default_factory=list)  # Optional. Fields to be displayed on the front of the pass
    backFields: typing.List[Field] = PydanticField(default_factory=list)  # Optional. Fields to be displayed on the back of the pass
    auxiliaryFields: typing.List[Field] = PydanticField(default_factory=list)  # Optional. Additional fields to be displayed on the front of the pass
    
    def addHeaderField(self, key, value, label):
        self.headerFields.append(Field(key, value, label))

    def addPrimaryField(self, key, value, label):
        self.primaryFields.append(Field(key, value, label))

    def addSecondaryField(self, key, value, label):
        self.secondaryFields.append(Field(key, value, label))

    def addBackField(self, key, value, label):
        self.backFields.append(Field(key, value, label))

    def addAuxiliaryField(self, key, value, label):
        self.auxiliaryFields.append(Field(key, value, label))


pass_model_registry = {}


def passmodel(name: str):
    def inner(cls):
        print("name", name)
        pass_model_registry[name] = cls
        cls._jsonname = name
        return cls
    
    return inner


@passmodel('boardingPass')
class BoardingPass(PassInformation):
    transitType: TransitType = TransitType.AIR
    

@passmodel('coupon')
class Coupon(PassInformation):
    pass
    

@passmodel('eventTicket')
class EventTicket(PassInformation):
    pass
    

@passmodel('generic')
class Generic(PassInformation):
    pass
    
    
@passmodel('storeCard')
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
    barcode: Barcode | None = PydanticField(default=None, deprecated=True, description="Use barcodes instead")
    """Optional. Information specific to the pass’s barcode. The system uses the first valid 
    barcode dictionary in the array. Additional dictionaries can be added as fallbacks."""
    
    # not really sure, need some examples for barcodes
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
    relevantDate: DateField | None = None
    """Optional. Date and time when the pass becomes relevant."""
    associatedStoreIdentifiers: list[str] | None = None
    """Optional. Identifies which merchants’ locations accept the pass."""
    
    appLaunchURL: str | None = None
    """Optional. A URL to be passed to the associated app when launching it."""
    userInfo: dict | None = None
    """Optional. Custom information for the pass."""
    expirationDate: DateField | None = None # TODO: check if this is correct
    """Optional. Date and time when the pass expires."""
    voided: bool = False
    
    @property
    def passInformation():
        """Returns the pass information object by checkinf all passmodel entries using all()"""
        raise NotImplementedError()
    
    
# hack in an optional field for each passmodel(passtype) since these are not known at compile time
for jsonname, cls in pass_model_registry.items():
    Pass.model_fields[jsonname] = FieldInfo(annotation=cls, required=False, default=None, exclude_none=True)
    
Pass.model_rebuild(force=True)
  
    
