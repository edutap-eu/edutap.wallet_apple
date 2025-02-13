from datetime import datetime
from datetime import timezone
from pydantic import BaseModel
from pydantic import Field


# Based on: https://developer.apple.com/documentation/walletpasses/adding-a-web-service-to-update-passes#Store-Information

# TODO: rename it to AppleDevice
class AppleDeviceRegistry(BaseModel):  # type: ignore[call-arg]
    """
    Contains the devices that contain updatable passes. Information for a device includes
    the device library identifier and the push token that your server uses
    to send update notifications.
    """

    deviceLibraryIdentifier: str
    pushToken: str
    registrationTime: datetime = Field(default=datetime.now(tz=timezone.utc))


# TODO: rename it to ApplePass
class ApplePassData(BaseModel):  # type: ignore[call-arg]
    """
    Contains the updatable passes. Information for a pass includes the pass type
    identifier, serial number, and a last-update tag. You define the contents of
    this tag and use it to track when you last updated a pass.
    The table can also include other data that you require to generate an updated pass.
    """

    passTypeIdentifier: str
    serialNumber: str
    lastUpdateTag: datetime = Field(default=datetime.now(tz=timezone.utc))


class ApplePassRegistration(BaseModel):  # type: ignore[call-arg]
    """
    Contains the relationships between passes and devices. Use this table to
    find the devices registered for a pass, and to find all the registered passes
    for a device. Both relationships are many-to-many.

     It can happen that a pass gets registered, but the passdata is not (yet) available.
     In this case the passdata will be created empty and filled later.
    """

    deviceLibraryIdentifier: str  # Foreign key to AppleDeviceRegistry
    passTypeIdentifier: str  # Forein key to ApplePassData
    serialNumber: str
    registrationTime: datetime = Field(default=datetime.now(tz=timezone.utc))
