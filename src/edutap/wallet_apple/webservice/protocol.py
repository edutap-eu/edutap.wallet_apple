from typing import Protocol, runtime_checkable, Any


PushToken = str
DeviceTypeIdentifier = str
SerialNumbers = list[str]

PassData = dict[str, Any]


@runtime_checkable
class PassRegistration(Protocol):
    """
    Protocol definition for an injectable PassRegistration handler.
    It will be used by the webservice to handle pass registration
    
    """

    def register_pass(self, pass_id: str, push_token: PushToken) -> None:
        """
        see https://developer.apple.com/documentation/walletpasses/register-a-pass-for-update-notifications
        """

    def unregister_pass(self, pass_id: str, push_token: PushToken) -> None: 
        """
        see https://developer.apple.com/documentation/walletpasses/unregister-a-pass-for-update-notifications
        """


@runtime_checkable
class PassDataAcquisition(Protocol):
    """
    Protocol definition for an injectable PassDataAcquisition handler
    """

    def fetch_pass_creation_data(self, pass_id: str) -> PassData: 
        """
        Fetches pass creation data from the database
        """

    def get_push_token(self, device_type_id: str, pass_type_id: str) -> PushToken:
        """
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
        retrieves the pass data necessary for pass creation
        """
        