# pylint: disable=unused-argument

# pylint: disable=redefined-outer-name
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
from common import apple_passes_dir
from common import generated_passes_dir
from edutap.wallet_apple import api
from edutap.wallet_apple.models import handlers
from edutap.wallet_apple.settings import Settings
from importlib import metadata
from importlib.metadata import EntryPoint
from pathlib import Path
from pydantic import Field
from typing import Callable

import json
import os
import pytest


try:
    from edutap.wallet_apple.handlers.fastapi import router
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    have_fastapi = True
except ImportError:
    have_fastapi = False
    raise


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
        prefix = self.model_config["env_prefix"]
        os.environ[prefix + "ROOT_DIR"] = str(self.root_dir)
        os.environ[prefix + "DATA_DIR"] = str(self.data_dir)
        os.environ[prefix + "CERT_DIR"] = str(self.cert_dir)


@pytest.fixture
def settings_fastapi():
    return SettingsTest()


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

    async def get_pass_data(self, pass_id: str) -> handlers.PassData:
        settings = SettingsTest()
        pass_path = settings.unsigned_passes_dir / f"{pass_id}.pkpass"
        assert pass_path.exists()
        with open(pass_path, "rb") as fh:
            pass1 = api.new(file=fh)
            return api.pkpass(pass1)

    async def get_push_tokens(
        self, device_type_id: str | None, pass_type_id: str, serial_number: str
    ) -> list[handlers.PushToken]:
        return []

    def test_get_update_serial_numbers(self):
        pass

    async def get_update_serial_numbers(
        self, device_type_id: str, pass_type_id: str, last_updated: str
    ) -> handlers.SerialNumbers:
        return handlers.SerialNumbers(
            serialNumers=["1234"], lastUpdated="2021-09-01T12:00:00Z"
        )


@pytest.fixture
def entrypoints_testing(monkeypatch) -> Callable:
    """
    fixture for mocking entrypoints for testing:

    - class TestPassRegistration
    - class TestPassDataAcquisition
    """
    eps = {
        "edutap.wallet_apple.plugins": [
            EntryPoint(
                name="PassRegistration",
                value="test_handlers_fastapi:TestPassRegistration",
                group="edutap.wallet_apple.handlers.fastapi.router",
            ),
            EntryPoint(
                name="PassDataAcquisition",
                value="test_handlers_fastapi:TestPassDataAcquisition",
                group="edutap.wallet_apple.handlers.fastapi.router",
            ),
        ]
    }

    def mock_entry_points(group: str):
        """
        replacement for the official `importlib.metadata.entry_points()` function
        """
        return eps.get(group, [])

    from edutap.wallet_apple import plugins

    monkeypatch.setattr(metadata, "entry_points", mock_entry_points)
    monkeypatch.setattr(plugins, "entry_points", mock_entry_points)
    return mock_entry_points


@pytest.fixture
def fastapi_client(entrypoints_testing) -> TestClient:
    """
    fixture for testing FastAPI with the router from edutap.wallet_apple.handlers.fastapi
    returns a TestClient instance ready for testing
    """
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


@pytest.fixture
def initial_unsigned_pass(generated_passes_dir) -> Path:
    """
    fixture for creating a new unsigned pass
    needed for testing `TestPassDataAcquisition.get_pass_data()`
    """
    settings = SettingsTest()
    pass_path = (
        settings.unsigned_passes_dir / f"{settings.initial_pass_serialnumber}.pkpass"
    )

    buf = open(settings.jsons_dir / "storecard_with_nfc.json").read()
    jdict = json.loads(buf)
    pass1 = api.new(data=jdict)

    pass1._add_file("icon.png", open(settings.resources_dir / "white_square.png", "rb"))

    # ofile = settings.unsigned_passes_dir / f"{settings.initial_pass_serialnumber}.pkpass"
    with api.pkpass(pass1) as zip_fh:
        with open(pass_path, "wb") as fh:
            fh.write(zip_fh.read())

    return pass_path


def test_entrypoints(entrypoints_testing):
    from edutap.wallet_apple.plugins import get_pass_data_acquisitions
    from edutap.wallet_apple.plugins import get_pass_registrations

    pr = get_pass_registrations()
    pd = get_pass_data_acquisitions()

    assert len(pr) > 0
    assert len(pd) > 0
    print(pr)


def test_initial_unsigned_pass(initial_unsigned_pass):
    assert initial_unsigned_pass.exists()


################################################
# Here come the real tests
################################################


@pytest.mark.skipif(not have_fastapi, reason="fastapi not installed")
def test_get_pass(entrypoints_testing, fastapi_client, settings_fastapi):
    # app = FastAPI()
    # app.include_router(router)
    # client = TestClient(app)
    response = fastapi_client.get("/apple_update_service/v1/passes/1234/1234")
    assert response.status_code == 200

    # TODO: extract pkpass file
    settings = SettingsTest()

    print(settings)
