from edutap.wallet_apple.models import handlers

import io


class TestPassRegistration:
    """
    Implementation of edutap.wallet_apple.protocols.PassRegistration
    """

    async def register_pass(
        self,
        device_id: str,
        pass_type_id: str,
        serial_number: str,
        push_token: handlers.PushToken,
    ) -> None: ...

    async def unregister_pass(
        self, device_id: str, pass_type_id: str, serial_number: str
    ) -> None: ...


class TestPassDataAcquisition:
    """
    Implementation of edutap.wallet_apple.protocols.PassDataAcquisition
    """

    async def get_pass_data(self, pass_id: str) -> handlers.PassData:
        return io.BytesIO()

    async def get_push_tokens(
        self, device_type_id: str | None, pass_type_id: str, serial_number: str
    ) -> list[handlers.PushToken]:
        return []

    async def get_update_serial_numbers(
        self, device_type_id: str, pass_type_id: str, last_updated: str
    ) -> handlers.SerialNumbers:
        return handlers.SerialNumbers(serialNumers=[], lastUpdated="never")
