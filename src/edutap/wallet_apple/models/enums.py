from enum import Enum


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
