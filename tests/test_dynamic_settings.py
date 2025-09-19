from edutap.wallet_apple import api
from edutap.wallet_apple.plugins import add_plugin
from edutap.wallet_apple.plugins import remove_plugins
from edutap.wallet_apple.settings import Settings
from plugins import SettingsTest

import pytest


settings = SettingsTest()
logger = settings.get_logger()


class TestDynamicSettings:

    def get_private_key(self, pass_type_identifier: str) -> bytes:
        """
        returns a private key depending on a pass type identifier
        """
        logger.info(
            "get_private_key",
            pass_type_identifier=pass_type_identifier,
            realm="dynamic-settings",
        )
        with open(settings.private_key, "rb") as fh:
            return fh.read()

    def get_pass_certificate(self, pass_type_identifier: str) -> bytes:
        """
        returns a private key depending on a pass type identifier
        """
        logger.info(
            "get_pass_certificate",
            pass_type_identifier=pass_type_identifier,
            realm="dynamic-settings",
        )
        with open(settings.get_certificate_path(pass_type_identifier), "rb") as fh:
            return fh.read()


@pytest.fixture
def dynamic_settings():
    """registers test plugin for dynamic settings"""

    add_plugin("DynamicSettings", TestDynamicSettings)
    yield
    # cleanup
    remove_plugins(TestDynamicSettings)


def test_dynamic_settings_sign_existing_generic_pass_and_get_bytes(
    apple_passes_dir,
    generated_passes_dir,
    pass_data_passthrough,
    dynamic_settings,
    settings_test: Settings,
    # pass_type_id: str,
    testlog,
):
    """
    test signing a pass with dynamic settings activated.
    we check the successful call of dynamic settings plugins
    by analysing the logs since the testing plugins write to the log.
    """
    pass_type_id = "pass.demo.lmu.de"
    with open(settings_test.root_dir / "unsigned-passes" / "1234.pkpass", "rb") as fh:
        pkpass = api.new(file=fh)
        pkpass.pass_object_safe.passTypeIdentifier = pass_type_id
        pkpass.pass_object_safe.teamIdentifier = settings_test.team_identifier

        fernet_key = b"AIYbyKUTkJpExGmNjEoI23AOqcMHIO7HhWPnMYKQWZA="  # TODO: softcode
        settings_test.fernet_key = fernet_key.decode("utf-8")
        token = api.create_auth_token(
            pkpass.pass_object_safe.passTypeIdentifier,
            "1234",  # TODO: serial number softcoded,
            # fernet_key=fernet_key,
        )
        pkpass.pass_object_safe.authenticationToken = token.decode("utf-8")
        pkpass.pass_object_safe.serialNumber = "1234"
        pkpass.pass_object_safe.webServiceURL = api.save_link(
            pkpass.pass_object_safe.passTypeIdentifier,
            pkpass.pass_object_safe.serialNumber,
            settings=settings_test,
        )
        api.sign(pkpass, settings=settings_test)
        assert pkpass.is_signed

    # test signing a pass and check the logs for the dynamic settings for get_private_key and get_pass_certificate
    logs = [
        log
        for log in testlog
        if log["realm"] == "dynamic-settings" and log["event"] == "get_private_key"
    ]

    assert len(logs) > 0

    logs = [
        log
        for log in testlog
        if log["realm"] == "dynamic-settings" and log["event"] == "get_pass_certificate"
    ]

    assert len(logs) > 0
