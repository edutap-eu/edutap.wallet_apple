# pylint: disable=unused-argument

# pylint: disable=redefined-outer-name
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
from common import apple_passes_dir  # noqa: F401
from common import generated_passes_dir  # noqa: F401
from common import key_files_exist
from edutap.wallet_apple import api
from edutap.wallet_apple.models import handlers
from email.parser import HeaderParser
from importlib import metadata
from importlib.metadata import EntryPoint
from io import BytesIO
from pathlib import Path
from edutap.wallet_apple.plugins import get_logging_handlers
from plugins import SettingsTest
from typing import Callable

import json
import os
import pytest


try:
    from edutap.wallet_apple.handlers.fastapi import router
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse
    from fastapi.testclient import TestClient

    have_fastapi = True
except ImportError:
    have_fastapi = False
    raise


@pytest.fixture
def settings_fastapi():
    return SettingsTest()


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
                value="plugins:TestPassRegistration",
                group="edutap.wallet_apple.handlers.fastapi.router",
            ),
            EntryPoint(
                name="PassDataAcquisition",
                value="plugins:TestPassDataAcquisition",
                group="edutap.wallet_apple.handlers.fastapi.router",
            ),
            EntryPoint(
                name="Logging",
                value="plugins:TestLogging",
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
def initial_unsigned_pass(generated_passes_dir) -> Path:  # noqa: F811
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
    logging = get_logging_handlers()

    assert len(pr) > 0
    assert len(pd) > 0
    assert len(logging) > 0
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
    assert pass2.pass_object_safe.passTypeIdentifier == settings_fastapi.pass_type_identifier
    assert pass2.pass_object_safe.description.startswith("changed")
    assert (
        pass2.pass_object_safe.passTypeIdentifier
        == settings_fastapi.pass_type_identifier
    )
    assert (
        pass2.pass_object_safe.webServiceURL
        == f"https://{settings_fastapi.domain}:{settings_fastapi.https_port}/apple_update_service"
    )
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
def test_uregister_pass(entrypoints_testing, fastapi_client, settings_fastapi):
    device_id = "a0ccefd5944f32bcae520d64c4dc7a16"
    response = fastapi_client.delete(
        f"/apple_update_service/v1/devices/{device_id}/registrations/{settings_fastapi.pass_type_identifier}/{1234}",
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


@pytest.mark.skipif(not key_files_exist(), reason="key and cert files missing")
@pytest.mark.skipif(not have_fastapi, reason="fastapi not installed")
def test_logging(entrypoints_testing, fastapi_client, settings_fastapi):
    response = fastapi_client.post(
        "/apple_update_service/v1/log",
        data=handlers.LogEntries(logs=["log1", "log2"]).model_dump_json(),
    )
    assert response.status_code == 200
    print(response.json())


@pytest.mark.skip("internal use only")
def test_start_server(entrypoints_testing, settings_fastapi):
    """
    only used for manual interactive testing with the handheld
    """

    import uvicorn  # type: ignore

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
