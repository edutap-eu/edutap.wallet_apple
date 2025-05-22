# pylint: disable=too-few-public-methods
from pydantic import BaseModel
from pydantic import ConfigDict
from typing import BinaryIO
from pydantic import EmailStr


DeviceTypeIdentifier = str
PassData = BinaryIO


class PushToken(BaseModel):
    """
    An object that contains the push notification token for a registered pass on a device.

    see: https://developer.apple.com/documentation/walletpasses/pushtoken
    """

    model_config = ConfigDict(  # control if instances can have extra attributes
        extra="forbid",
    )
    pushToken: str
    deviceLibraryIdentifier: DeviceTypeIdentifier | None = None
    passTypeIdentifier: str | None = None


class SerialNumbers(BaseModel):
    """
    An object that contains serial numbers for the updatable passes on a device.

    see: https://developer.apple.com/documentation/walletpasses/serialnumbers
    """

    serialNumbers: list[str]
    lastUpdated: str
    """A developer-defined string that contains a tag that indicates the modification time for the returned passes."""


class LogEntries(BaseModel):
    """
    An object that contains a list of messages.

    see: https://developer.apple.com/documentation/walletpasses/logentries
    """

    model_config = ConfigDict(  # control if instances can have extra attributes
        extra="allow",
    )
    logs: list[str] = []


class RequiredPersonalizationInfo(BaseModel):
    """
    An object that contains the user-entered information for a personalized pass.
    see: https://developer.apple.com/documentation/walletpasses/personalizationdictionary/requiredpersonalizationinfo-data.dictionary
    """

    model_config = ConfigDict(  # control if instances can have extra attributes
        extra="allow",
    )

    # Attribute order as in Apple's documentation to make future changes easier!
    # last checked: 2025-05-21

    emailAddress: EmailStr | None = None
    """
    string
    The user-entered email address for the user of the personalized pass.
    """

    familyName: str | None = None
    """
    string
    The family name for the user of the personalized pass, parsed from the full name. The name can indicate membership in a group.
    """

    fullName: str | None = None
    """
    string
    The user-entered full name for the user of the personalized pass.
    """

    givenName: str | None = None
    """
    string
    The given name for the user of the personalized pass, parsed from the full name. The system uses the name to differentiate the individual from other members who share the same family name. In some locales, the given name is also known as a forename or first name.
    """

    ISOCountryCode: str | None = None
    """
    string
    The ISO country code. The system sets this key when it’s known; otherwise, it doesn’t include the key.
    """

    phoneNumber: str | None = None
    """
    string
    The user-entered phone number for the user of the personalized pass.
    """

    postalCode : str | None = None
    """
    string
    The user-entered postal code for the user of the personalized pass.
    """


class PersonalizationDictionary(BaseModel):
    """
    see https://developer.apple.com/documentation/walletpasses/personalizationdictionary
    """
    model_config = ConfigDict(  # control if instances can have extra attributes
        extra="forbid",
    )

    personalizationToken: str
    """
    Required.
    The personalization token for this request. The server must sign and return the token.
    """

    requiredPersonalizationInfo: RequiredPersonalizationInfo
    """
    Required.
    An object that contains the user-entered information for a personalized pass.
    """