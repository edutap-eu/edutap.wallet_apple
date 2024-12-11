# pylint: disable=too-few-public-methods
from pydantic import BaseModel
from pydantic import ConfigDict
from typing import BinaryIO


DeviceTypeIdentifier = str
PassData = BinaryIO


class PushToken(BaseModel):
    """
    An object that contains the push notification token for a registered pass on a device.

    see: https://developer.apple.com/documentation/walletpasses/pushtoken
    """

    model_config = ConfigDict(  # control if instances can have extra attributes
        extra="forbid",
        # extra="ignore",
        # extra="allow",
    )
    pushToken: str


class SerialNumbers(BaseModel):
    """
    An object that contains serial numbers for the updatable passes on a device.

    see: https://developer.apple.com/documentation/walletpasses/serialnumbers
    """

    serialNumers: list[str]
    lastUpdated: str
    """A developer-defined string that contains a tag that indicates the modification time for the returned passes."""


class LogEntries(BaseModel):
    """
    An object that contains a list of messages.

    see: https://developer.apple.com/documentation/walletpasses/logentries
    """

    model_config = ConfigDict(  # control if instances can have extra attributes
        # extra="forbid",
        # extra="ignore",
        extra="allow",
    )
    logs: list[str] = []


class PersonalizationDictionary(BaseModel):
    """
    see https://developer.apple.com/documentation/walletpasses/personalizationdictionary
    """
