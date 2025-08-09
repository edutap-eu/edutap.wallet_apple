from edutap.wallet_apple.models import handlers
from edutap.wallet_apple.plugins import add_plugin
from edutap.wallet_apple.plugins import get_logging_handlers
from edutap.wallet_apple.plugins import get_pass_data_acquisitions
from edutap.wallet_apple.plugins import get_pass_registrations
from edutap.wallet_apple.plugins import remove_plugins

import pytest


class DummyPassRegistration:
    async def pass_registration(self):
        pass

    async def register_pass(
        self,
        device_libray_id: str,
        pass_type_id: str,
        serial_number: str,
        push_token: handlers.PushToken | None,
    ) -> None: ...

    async def unregister_pass(
        self, device_library_id: str, pass_type_id: str, serial_number: str
    ) -> None: ...


class DummyPassDataAcquisition:
    async def get_pass_data(
        self, *, pass_type_id: str | None, serial_number: str, update: bool = False
    ) -> handlers.PassData:
        raise NotImplementedError

    async def get_push_tokens(
        self, device_library_id: str | None, pass_type_id: str, serial_number: str
    ) -> list[handlers.PushToken]:
        raise NotImplementedError

    async def get_update_serial_numbers(
        self, device_library_id: str, pass_type_id: str, last_updated: str | None = None
    ) -> handlers.SerialNumbers:
        raise NotImplementedError

    async def check_authentication_token(
        self, pass_type_id: str | None, serial_number: str | None, token: str
    ) -> bool:
        raise NotImplementedError


class DummyLogging:
    async def log(self, entries: handlers.LogEntries) -> None: ...


def test_get_pass_registrations(entrypoints_testing):
    from edutap.wallet_apple.plugins import get_pass_registrations
    from edutap.wallet_apple.protocols import PassRegistration

    plugins = get_pass_registrations()
    assert len(plugins) == 2
    assert isinstance(plugins[0], PassRegistration)


def test_get_pass_data_acquisitions(entrypoints_testing):
    from edutap.wallet_apple.plugins import get_pass_data_acquisitions
    from edutap.wallet_apple.protocols import PassDataAcquisition

    plugins = get_pass_data_acquisitions()
    assert len(plugins) == 1
    assert isinstance(plugins[0], PassDataAcquisition)


def test_get_logging_handlers(entrypoints_testing):
    from edutap.wallet_apple.plugins import get_logging_handlers
    from edutap.wallet_apple.protocols import Logging

    plugins = get_logging_handlers()
    assert len(plugins) == 2
    assert isinstance(plugins[0], Logging)


def test_add_plugin():
    try:
        count_pass_registrations = len(get_pass_registrations())
    except NotImplementedError:
        count_pass_registrations = 0
    try:
        count_pass_data_acquisitions = len(get_pass_data_acquisitions())
    except NotImplementedError:
        count_pass_data_acquisitions = 0
    try:
        count_logging_handlers = len(get_logging_handlers())
    except NotImplementedError:
        count_logging_handlers = 0

    add_plugin("PassRegistration", DummyPassRegistration)

    # check for TypeError for wrong plugin type
    with pytest.raises(TypeError):
        add_plugin("PassDataAcquisition", DummyPassRegistration)
    add_plugin("PassDataAcquisition", DummyPassDataAcquisition)
    add_plugin("Logging", DummyLogging)

    assert len(get_pass_registrations()) == count_pass_registrations + 1
    assert len(get_pass_data_acquisitions()) == count_pass_data_acquisitions + 1
    assert len(get_logging_handlers()) == count_logging_handlers + 1

    remove_plugins(DummyPassDataAcquisition, DummyPassRegistration, DummyLogging)

    assert len(get_pass_registrations()) == count_pass_registrations
    assert len(get_pass_data_acquisitions()) == count_pass_data_acquisitions
    assert len(get_logging_handlers()) == count_logging_handlers
