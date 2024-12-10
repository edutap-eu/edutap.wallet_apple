from typing import Protocol, runtime_checkable, Any

from pydantic import BaseModel, ConfigDict


DeviceTypeIdentifier = str
PassData = dict[str, Any]


class PushToken(BaseModel):
    """
    An object that contains the push notification token for a registered pass on a device.

    see: https://developer.apple.com/documentation/walletpasses/pushtoken
    """

    model_config = ConfigDict( # control if instances can have extra attributes
        # extra="forbid",
        # extra="ignore",
        extra="allow",
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


@runtime_checkable
class PassRegistration(Protocol):
    """
    Protocol definition for an injectable PassRegistration handler.
    It will be used by the webservice to handle pass registration
    
    """

    def register_pass(self, device_id: str, pass_type_id: str, serial_number:str, push_token: PushToken) -> None:
        """
        see https://developer.apple.com/documentation/walletpasses/register-a-pass-for-update-notifications
        """

    def unregister_pass(self,device_id: str, pass_type_id: str, serial_umber: str) -> None: 
        """
        see https://developer.apple.com/documentation/walletpasses/unregister-a-pass-for-update-notifications
        """


@runtime_checkable
class PassDataAcquisition(Protocol):
    """
    Protocol definition for an injectable PassDataAcquisition handler
    """

    def get_pass_creation_data(self, pass_id: str) -> PassData: 
        """
        Fetches pass creation data from the database
        is called by the Edutap Apple Provider upon creation of a new pass
        
        TODO: specify the parameters
        """

    def get_push_token(self, device_type_id: str, pass_type_id: str, serial_number: str) -> PushToken:
        """
        called during pass update,
        returns a push token
        see https://developer.apple.com/documentation/walletpasses/pushtoken
        """

    def get_update_serial_numbers(
        self, device_type_id: str, pass_type_id: str, last_updated: str
    ) -> SerialNumbers: 
        """
        Fetches the serial numbers of the passes that have been updated since the last update
        see https://developer.apple.com/documentation/walletpasses/get-the-list-of-updatable-passes
        """

    def get_pass_data(self, device_type_id: str, pass_type_id: str, serial_number: str) -> PassData: 
        """
        retrieves the pass data necessary for pass update for a sinngle pass
        """
        

class LogEntries(BaseModel):
    """
    An object that contains a list of messages.

    see: https://developer.apple.com/documentation/walletpasses/logentries
    """

    model_config = ConfigDict( # control if instances can have extra attributes
        # extra="forbid",
        # extra="ignore",
        extra="allow",
    )
    logs: list[str] = []
