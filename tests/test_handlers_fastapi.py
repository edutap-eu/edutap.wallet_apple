# pylint: disable=unused-argument

# pylint: disable=redefined-outer-name
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
from email.parser import HeaderParser
from io import BytesIO

from common import apple_passes_dir, key_files_exist
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
    from fastapi.responses import HTMLResponse

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
        self.pass_type_identifier = "pass.demo.lmu.de"
        self.team_identifier = "JG943677ZY"
        self.https_port = 8080
        self.domain = "localhost"
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
        """
        fetch the unsigned pass by its pass_id from a given folder
        """
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


@pytest.mark.skipif(not key_files_exist(), reason="key and cert files missing")
@pytest.mark.skipif(not have_fastapi, reason="fastapi not installed")
def test_get_pass(entrypoints_testing, fastapi_client, settings_fastapi):
    response = fastapi_client.get(
        f"/apple_update_service/v1/passes/{settings_fastapi.pass_type_identifier}/{settings_fastapi.initial_pass_serialnumber}"
    )
    assert response.status_code == 200

    cd = response.headers.get("content-disposition")
    parser = HeaderParser()
    headers = parser.parsestr(f"Content-Disposition: {cd}")
    filename = headers.get_param("filename", header="Content-Disposition")

    # TODO: extract pkpass file
    assert len(response.content) > 0
    fh = BytesIO(response.content)
    out = settings_fastapi.signed_passes_dir / filename
    with open(out, "wb") as fp:
        fp.write(response.content)
        os.system(f"open {out}")

    # parse the pass and check values
    fh.seek(0)
    pass2 = api.new(file=fh)
    assert pass2.is_signed
    assert pass2.pass_object_safe.teamIdentifier == settings_fastapi.team_identifier
    assert (
        pass2.pass_object_safe.passTypeIdentifier
        == settings_fastapi.pass_type_identifier
    )
    assert pass2.pass_object_safe.webServiceURL == f"https://{settings_fastapi.domain}:{settings_fastapi.https_port}/apple_update_service"
    print(pass2)


@pytest.mark.skipif(not key_files_exist(), reason="key and cert files missing")
@pytest.mark.skipif(not have_fastapi, reason="fastapi not installed")
def test_register_pass(entrypoints_testing, fastapi_client, settings_fastapi):
    device_id = "a0ccefd5944f32bcae520d64c4dc7a16"
    response = fastapi_client.post(
        f"/apple_update_service/v1/devices/{device_id}/registrations/{settings_fastapi.pass_type_identifier}/{1234}",
        data=handlers.PushToken(pushToken="333333").model_dump_json(),
    )
    assert response.status_code == 200

@pytest.mark.skipif(not key_files_exist(), reason="key and cert files missing")
@pytest.mark.skipif(not have_fastapi, reason="fastapi not installed")
def test_list_updateable_passes(entrypoints_testing, fastapi_client, settings_fastapi):
    device_id = "a0ccefd5944f32bcae520d64c4dc7a16"
    response = fastapi_client.get(
        f"/apple_update_service/v1/devices/{device_id}/registrations/{settings_fastapi.pass_type_identifier}?passesUpdatedSince=letztens"
    )
    serial_numbers = handlers.SerialNumbers.model_validate(response.json())
    assert serial_numbers.serialNumers == ["1234"]
    assert serial_numbers.lastUpdated == "2021-09-01T12:00:00Z"
    assert response.status_code == 200


@pytest.mark.skip("internal use only")
def test_start_server(entrypoints_testing, settings_fastapi):
    """
    only used for manual interactive testing with the handheld
    """
    import uvicorn

    app = FastAPI()
    app.include_router(router)

    @app.get("/", response_class=HTMLResponse)
    async def read_root():
        html_content = f"""
        <html>
            <head>
                <title>Sample HTML Page</title>
            </head>
            <body>
                <h1>Hello, World!</h1>
                <a href={router.prefix}/passes/{settings_fastapi.pass_type_identifier}/{settings_fastapi.initial_pass_serialnumber}>Get Pass</a>
            </body>
        </html>
        """
        return HTMLResponse(content=html_content, status_code=200)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        # ssl_keyfile=settings_fastapi.cert_dir / "ssl" / "key.pem",
        # ssl_certfile=settings_fastapi.cert_dir / "ssl" / "cert.pem",
    )
