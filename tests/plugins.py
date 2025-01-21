# pylint: disable=missing-function-docstring
# pylint: disable=too-few-public-methods
# pylint: disable=unused-argument
# pylint: disable=missing-class-docstring

from datetime import datetime
from edutap.wallet_apple import api
from edutap.wallet_apple.models import handlers
from edutap.wallet_apple.settings import Settings
from pathlib import Path
from pydantic import Field

import os


class SettingsTest(Settings):
    data_dir: Path = Field(default_factory=lambda dd: dd["root_dir"] / "tests" / "data")
    """directory where the test data is stored"""
    unsigned_passes_dir: Path = Field(
        default_factory=lambda dd: dd["data_dir"] / "unsigned-passes"
    )
    signed_passes_dir: Path = Field(
        default_factory=lambda dd: dd["data_dir"] / "signed-passes"
    )
    jsons_dir: Path = Field(default_factory=lambda dd: dd["data_dir"] / "jsons")
    initial_pass_serialnumber: str = "1234"
    resources_dir: Path = Field(default_factory=lambda dd: dd["data_dir"] / "resources")

    def __init__(self, **kw):
        super().__init__(**kw)

        print("init done")
        # make sure that the directories exist
        self.unsigned_passes_dir.mkdir(parents=True, exist_ok=True)
        self.signed_passes_dir.mkdir(parents=True, exist_ok=True)
        self.cert_dir = self.data_dir / "certs" / "private"
        self.pass_type_identifier = "pass.demo.lmu.de"
        self.team_identifier = "JG943677ZY"
        self.https_port = 443
        self.domain = "localhost"
        self.fernet_key = "AIYbyKUTkJpExGmNjEoI23AOqcMHIO7HhWPnMYKQWZA="
    
        prefix = self.model_config["env_prefix"]

        # is needed, so that the settings are correct in
        # eduap.wallet_apple.api and edutap.wallet.handlers.fastapi
        os.environ[prefix + "ROOT_DIR"] = str(self.root_dir)
        os.environ[prefix + "DATA_DIR"] = str(self.data_dir)
        os.environ[prefix + "CERT_DIR"] = str(self.cert_dir)
        os.environ[prefix + "TEAM_IDENTIFIER"] = str(self.team_identifier)
        os.environ[prefix + "PASS_TYPE_IDENTIFIER"] = str(self.pass_type_identifier)
        os.environ[prefix + "HTTPS_PORT"] = str(self.https_port)
        os.environ[prefix + "DOMAIN"] = str(self.domain)
        os.environ[prefix + "FERNET_KEY"] = 'AIYbyKUTkJpExGmNjEoI23AOqcMHIO7HhWPnMYKQWZA='


class TestPassRegistration:
    """
    test plugin implementation for the `PassRegistration` protocol
    works on a local directory and does not need a real device.

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
    test plugin implementation for the `PassDataAcquisition` protocol
    works on a local directory and does not need a real device.
    """

    async def get_pass_data(
        self,
        *,
        pass_type_id: str | None = None,
        serial_number: str,
        update: bool = False,
    ) -> handlers.PassData:
        """
        fetch the unsigned pass by its pass_id from a given folder
        """
        settings = SettingsTest()
        pass_path = settings.unsigned_passes_dir / f"{serial_number}.pkpass"
        assert pass_path.exists()
        with open(pass_path, "rb") as fh:
            pass1 = api.new(file=fh)
            if pass_type_id is not None:
                pass1.pass_object_safe.passTypeIdentifier = pass_type_id
                
            pass1.pass_object_safe.description = f"changed {datetime.now()}"
            pass1.pass_object_safe.pass_information.secondaryFields[0].label = (
                f"payload {datetime.now()}"
            )
            if not update:
                token = api.create_auth_token(pass1.pass_object_safe.passTypeIdentifier, serial_number)
                pass1.pass_object_safe.authenticationToken = token
            pass1.pass_object_safe.serialNumber = serial_number
            
            return api.pkpass(pass1)

    async def get_push_tokens(
        self, device_type_id: str | None, pass_type_id: str, serial_number: str
    ) -> list[handlers.PushToken]:
        return []

    async def get_update_serial_numbers(
        self, device_type_id: str, pass_type_id: str, last_updated: str
    ) -> handlers.SerialNumbers:
        return handlers.SerialNumbers(
            serialNumers=["1234"], lastUpdated="2021-09-01T12:00:00Z"
        )

    async def check_authentication_token(
        self, pass_type_id: str | None, serial_number: str | None, token: str
    ) -> bool:
        """
        checks if a given authentication token is valid
        """
        pid, sn = api.extract_auth_token(token)
        return pid == pass_type_id and sn == serial_number


class TestLogging:
    """
    test plugin implementation for the `Logging` protocol
    """

    async def log(self, entries: handlers.LogEntries) -> None:
        for entry in entries.logs:
            print(f"logger :{entry}")
