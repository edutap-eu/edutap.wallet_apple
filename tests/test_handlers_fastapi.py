# pylint: disable=unused-argument

# pylint: disable=redefined-outer-name
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
from conftest import key_files_exist
from conftest import load_pass_viewer
from edutap.wallet_apple import api
from edutap.wallet_apple.models import handlers
from edutap.wallet_apple.plugins import get_logging_handlers
from email.parser import HeaderParser
from io import BytesIO
from pathlib import Path
from plugins import SettingsTest

import json
import pytest


settings = SettingsTest()

try:
    from edutap.wallet_apple.handlers.fastapi import router_apple_wallet
    from edutap.wallet_apple.handlers.fastapi import router_download_pass
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
def fastapi_client(entrypoints_testing) -> TestClient:
    """
    fixture for testing FastAPI with the router from edutap.wallet_apple.handlers.fastapi
    returns a TestClient instance ready for testing
    """
    app = FastAPI()
    app.include_router(router_apple_wallet)
    app.include_router(router_download_pass)
    return TestClient(app)


@pytest.fixture
def fastapi_client_passthrough(entrypoints_testing, monkeypatch) -> TestClient:
    """
    fixture for testing FastAPI with the router from edutap.wallet_apple.handlers.fastapi
    returns a TestClient instance ready for testing
    """

    monkeypatch.setenv(
        "EDUTAP_WALLET_APPLE_PASS_DATA_PASSTHROUGH","true",
    )

    app = FastAPI()
    app.include_router(router_apple_wallet)
    app.include_router(router_download_pass)
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
    logging = get_logging_handlers()

    assert len(pr) > 0
    assert len(pd) > 0
    assert len(logging) > 0
    print(pr)


def test_initial_unsigned_pass(initial_unsigned_pass):
    assert initial_unsigned_pass.exists()


def test_auth_key_encryption(settings_fastapi):
    pass_type_identifier = "pass.demo.lmu.de"
    serial_number = "1234"
    fernet_key = b"AIYbyKUTkJpExGmNjEoI23AOqcMHIO7HhWPnMYKQWZA="

    key = api.create_auth_token(pass_type_identifier, serial_number, fernet_key)
    assert key is not None

    # extract token as bytes
    id, sn = api.extract_auth_token(key, fernet_key)
    assert id == pass_type_identifier
    assert sn == serial_number

    # extract token as string
    id, sn = api.extract_auth_token(key, fernet_key.decode())
    assert id == pass_type_identifier
    assert sn == serial_number


def test_auth_key_encryption_fernet_key_from_settings(settings_fastapi):
    pass_type_identifier = "pass.demo.lmu.de"
    serial_number = "1234"

    key = api.create_auth_token(pass_type_identifier, serial_number)
    assert key is not None

    # extract token as bytes
    id, sn = api.extract_auth_token(key)
    assert id == pass_type_identifier
    assert sn == serial_number

    # extract token as string
    id, sn = api.extract_auth_token(key)
    assert id == pass_type_identifier
    assert sn == serial_number


def test_save_link(settings_fastapi):
    pass_type_identifier = "pass.demo.lmu.de"
    serial_number = "1234"
    link = api.save_link(pass_type_identifier, serial_number, schema="http")
    assert link is not None
    assert link.startswith("http://localhost/apple_update_service/v1/download-pass/")


################################################
# Here come the real tests
################################################


@pytest.mark.skipif(not key_files_exist(), reason="key and cert files missing")
@pytest.mark.skipif(not have_fastapi, reason="fastapi not installed")
@pytest.mark.parametrize(
    "pass_type_id", settings.get_available_passtype_ids()
)  # ["pass.demo.lmu.de", "pass.demo.library.lmu.de"])
def test_get_pass(
    entrypoints_testing,
    fastapi_client,
    settings_fastapi,
    pass_type_id,
    testlog,
):
    serial_number = settings_fastapi.initial_pass_serialnumber
    download_link = api.save_link(
        pass_type_id=pass_type_id,
        serial_number=settings_fastapi.initial_pass_serialnumber,
        schema="http",
    )

    response = fastapi_client.get(download_link)

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
        load_pass_viewer(out)

    # parse the pass and check values
    fh.seek(0)
    pass2 = api.new(file=fh)
    assert pass2.is_signed
    assert pass2.pass_object_safe.teamIdentifier == settings_fastapi.team_identifier
    assert pass2.pass_object_safe.passTypeIdentifier == pass_type_id
    assert pass2.pass_object_safe.description.startswith("changed")
    assert pass2.pass_object_safe.passTypeIdentifier == pass_type_id
    assert pass2.pass_object_safe.serialNumber == serial_number
    assert (
        pass2.pass_object_safe.webServiceURL
        == f"https://{settings_fastapi.domain}:{settings_fastapi.https_port}/apple_update_service"
    )

    # check the logs
    logs = [
        log
        for log in testlog
        if log["realm"] == "fastapi" and log["event"] == "download_pass"
    ]
    assert len(logs) == 1

    print(pass2)


@pytest.mark.skipif(not key_files_exist(), reason="key and cert files missing")
@pytest.mark.skipif(not have_fastapi, reason="fastapi not installed")
def test_get_updated_pass(
    entrypoints_testing, fastapi_client, settings_fastapi, testlog
):
    # give it a correct authorization token (normally the handheld would do that based on the auth token in the pass)
    # we have to fake it here
    token = api.create_auth_token(
        settings_fastapi.pass_type_identifier,
        settings_fastapi.initial_pass_serialnumber,
    ).decode("utf-8")

    response = fastapi_client.get(
        f"/apple_update_service/v1/passes/{settings_fastapi.pass_type_identifier}/{settings_fastapi.initial_pass_serialnumber}",
    )
    assert response.status_code == 401

    response = fastapi_client.get(
        f"/apple_update_service/v1/passes/{settings_fastapi.pass_type_identifier}/{settings_fastapi.initial_pass_serialnumber}",
        headers={"authorization": f"ApplePass {token}"},
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
        load_pass_viewer(out)

    # parse the pass and check values
    fh.seek(0)
    pass2 = api.new(file=fh)
    assert pass2.is_signed
    assert pass2.pass_object_safe.teamIdentifier == settings_fastapi.team_identifier
    assert (
        pass2.pass_object_safe.passTypeIdentifier
        == settings_fastapi.pass_type_identifier
    )
    assert pass2.pass_object_safe.description.startswith("changed")
    assert (
        pass2.pass_object_safe.passTypeIdentifier
        == settings_fastapi.pass_type_identifier
    )
    assert (
        pass2.pass_object_safe.webServiceURL
        == f"https://{settings_fastapi.domain}:{settings_fastapi.https_port}/apple_update_service"
    )

    # check the logs
    logs = [
        log
        for log in testlog
        if log["realm"] == "fastapi" and log["event"] == "get_updated_pass"
    ]
    assert len(logs) == 1

    # the failed authentication should be logged
    errlogs = [
        log
        for log in testlog
        if log["realm"] == "fastapi" and log["event"] == "check_authorization_failure"
    ]
    assert len(errlogs) == 1

    print(pass2)

@pytest.mark.skipif(not key_files_exist(), reason="key and cert files missing")
@pytest.mark.skipif(not have_fastapi, reason="fastapi not installed")
def test_get_updated_pass_with_passdata_passthrough(
    entrypoints_testing, fastapi_client_passthrough, settings_fastapi, testlog
):
    """
    this test checks getting a pass without preparing personal data and signing.
    Usecase is that the pass is readily signed and prepared on the client side
    in order to avoid additional ping-pongs in communication.
    """

    fastapi_client = fastapi_client_passthrough

    # give it a correct authorization token (normally the handheld would do that based on the auth token in the pass)
    # we have to fake it here
    token = api.create_auth_token(
        settings_fastapi.pass_type_identifier,
        settings_fastapi.initial_pass_serialnumber,
    ).decode("utf-8")

    response = fastapi_client.get(
        f"/apple_update_service/v1/passes/{settings_fastapi.pass_type_identifier}/{settings_fastapi.initial_pass_serialnumber}",
    )
    assert response.status_code == 401

    response = fastapi_client.get(
        f"/apple_update_service/v1/passes/{settings_fastapi.pass_type_identifier}/{settings_fastapi.initial_pass_serialnumber}",
        headers={"authorization": f"ApplePass {token}"},
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
        load_pass_viewer(out)

    # parse the pass and check values
    fh.seek(0)
    pass2 = api.new(file=fh)

    # since we have pass_data_passthrough the pass is not yet 
    assert not pass2.is_signed

    # check the logs
    logs = [
        log
        for log in testlog
        if log["realm"] == "fastapi" and log["event"] == "get_updated_pass"
    ]
    assert len(logs) == 1

    # the failed authentication should be logged
    errlogs = [
        log
        for log in testlog
        if log["realm"] == "fastapi" and log["event"] == "check_authorization_failure"
    ]
    assert len(errlogs) == 1

    print(pass2)


@pytest.mark.skipif(not key_files_exist(), reason="key and cert files missing")
@pytest.mark.skipif(not have_fastapi, reason="fastapi not installed")
def test_register_pass(entrypoints_testing, fastapi_client, settings_fastapi, testlog):
    device_id = "a0ccefd5944f32bcae520d64c4dc7a16"
    # give it a correct authorization token (normally the handheld would do that based on the auth token in the pass)
    # we have to fake it here
    token = api.create_auth_token(
        settings_fastapi.pass_type_identifier,
        settings_fastapi.initial_pass_serialnumber,
    ).decode("utf-8")

    # without auth token it should fail
    response = fastapi_client.post(
        f"/apple_update_service/v1/devices/{device_id}/registrations/{settings_fastapi.pass_type_identifier}/{1234}",
        data=handlers.PushToken(pushToken="333333").model_dump_json(),
    )
    assert response.status_code == 401

    response = fastapi_client.post(
        f"/apple_update_service/v1/devices/{device_id}/registrations/{settings_fastapi.pass_type_identifier}/{1234}",
        data=handlers.PushToken(pushToken="333333").model_dump_json(),
        headers={"authorization": f"ApplePass {token}"},
    )
    assert response.status_code == 200

    logs = [
        log
        for log in testlog
        if log["realm"] == "fastapi" and log["event"] == "register_pass"
    ]
    assert len(logs) >= 1

    handlerlogs = [
        log
        for log in testlog
        if log["realm"] == "handlers" and log["event"] == "register_pass"
    ]

    assert len(handlerlogs) == 2

    # the failed authentication should be logged
    errlogs = [
        log
        for log in testlog
        if log["realm"] == "fastapi" and log["event"] == "check_authorization_failure"
    ]
    assert len(errlogs) == 1


@pytest.mark.skipif(not key_files_exist(), reason="key and cert files missing")
@pytest.mark.skipif(not have_fastapi, reason="fastapi not installed")
def test_unregister_pass(
    entrypoints_testing, fastapi_client, settings_fastapi, testlog
):
    device_id = "a0ccefd5944f32bcae520d64c4dc7a16"
    # give it a correct authorization token (normally the handheld would do that based on the  auth token in the pass)
    # we have to fake it here
    token = api.create_auth_token(
        settings_fastapi.pass_type_identifier,
        settings_fastapi.initial_pass_serialnumber,
    ).decode("utf-8")

    # without auth token it should fail
    response = fastapi_client.delete(
        f"/apple_update_service/v1/devices/{device_id}/registrations/{settings_fastapi.pass_type_identifier}/{1234}",
    )
    assert response.status_code == 401

    response = fastapi_client.delete(
        f"/apple_update_service/v1/devices/{device_id}/registrations/{settings_fastapi.pass_type_identifier}/{1234}",
        headers={"authorization": f"ApplePass {token}"},
    )
    assert response.status_code == 200

    logs = [
        log
        for log in testlog
        if log["realm"] == "fastapi" and log["event"] == "unregister_pass"
    ]
    assert len(logs) == 1

    handlerlogs = [
        log
        for log in testlog
        if log["realm"] == "handlers" and log["event"] == "unregister_pass"
    ]

    assert len(handlerlogs) == 2

    # the failed authentication should be logged
    errlogs = [
        log
        for log in testlog
        if log["realm"] == "fastapi" and log["event"] == "check_authorization_failure"
    ]
    assert len(errlogs) == 1


@pytest.mark.skipif(not key_files_exist(), reason="key and cert files missing")
@pytest.mark.skipif(not have_fastapi, reason="fastapi not installed")
@pytest.mark.parametrize(
    "last_updated_since", [None, "2021-09-01T12:00:00Z", "letztens"]
)  # ["pass.demo.lmu.de", "pass.demo.library.lmu.de"])
def test_list_updateable_passes(
    entrypoints_testing,
    fastapi_client,
    settings_fastapi,
    testlog,
    last_updated_since,
):
    device_id = "a0ccefd5944f32bcae520d64c4dc7a16"
    url = (
        f"/apple_update_service/v1/devices/{device_id}/registrations/{settings_fastapi.pass_type_identifier}?passesUpdatedSince={last_updated_since}"
        if last_updated_since
        else f"/apple_update_service/v1/devices/{device_id}/registrations/{settings_fastapi.pass_type_identifier}"
    )
    response = fastapi_client.get(url)
    serial_numbers = handlers.SerialNumbers.model_validate(response.json())
    assert serial_numbers.serialNumbers == ["1234"]
    assert serial_numbers.lastUpdated == "2021-09-01T12:00:00Z"
    assert response.status_code == 200

    logs = [
        log
        for log in testlog
        if log["realm"] == "fastapi" and log["event"] == "list_updatable_passes"
    ]
    assert len(logs) == 2


@pytest.mark.skipif(not key_files_exist(), reason="key and cert files missing")
@pytest.mark.skipif(not have_fastapi, reason="fastapi not installed")
def test_logging(entrypoints_testing, fastapi_client, settings_fastapi, testlog):
    response = fastapi_client.post(
        "/apple_update_service/v1/log",
        data=handlers.LogEntries(logs=["log1", "log2"]).model_dump_json(),
    )
    assert response.status_code == 200
    print(response.json())

    handlerlogs = [
        log for log in testlog if log["realm"] == "handlers" and log["event"] == "log"
    ]

    # two logs ad two handlers give 4 logs to be there
    assert len(handlerlogs) == 4


@pytest.mark.skip("internal use only")
def test_start_server(entrypoints_testing, settings_fastapi):
    """
    only used for manual interactive testing with the handheld
    """

    import uvicorn  # type: ignore

    app = FastAPI()
    app.include_router(router_apple_wallet)

    @app.get("/", response_class=HTMLResponse)
    async def read_root():
        html_content = f"""
        <html>
            <head>
                <title>Sample HTML Page</title>
            </head>
            <body>
                <h1>Hello, World!</h1>
                <a href={router_apple_wallet.prefix}/passes/{settings_fastapi.pass_type_identifier}/{settings_fastapi.initial_pass_serialnumber}>Get Pass</a>
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
