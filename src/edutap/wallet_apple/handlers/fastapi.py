import datetime

import cryptography
from ..settings import Settings
from edutap.wallet_apple import api
from edutap.wallet_apple.models.handlers import LogEntries
from edutap.wallet_apple.models.handlers import PushToken
from edutap.wallet_apple.models.handlers import SerialNumbers
from edutap.wallet_apple.plugins import get_logging_handlers
from edutap.wallet_apple.plugins import get_pass_data_acquisitions
from edutap.wallet_apple.plugins import get_pass_registrations
from fastapi import APIRouter, HTTPException
from fastapi import Depends
from fastapi import Header
from fastapi import Request
from fastapi.concurrency import asynccontextmanager
from fastapi.responses import StreamingResponse
from typing import Annotated

import httpx  # type: ignore
import ssl


def get_settings() -> Settings:
    """
    TODO
    """
    res = Settings()

    return res


@asynccontextmanager
async def lifespan(router: APIRouter):
    # setup phase
    yield
    # shutdown


router = APIRouter(
    prefix="/apple_update_service/v1",
    lifespan=lifespan,
)


async def check_authorization(
    authorization: str | None,
    pass_type_identifier: str | None = None,
    serial_number: str | None = None,
) -> None:
    """
    check the authorization token as it comes in the request header for
    `register_pass`, `unregister_pass` and `get_pass` endpoints
    the autorizatio string is of the form `ApplePass <authenticationToken>`
    where the authotizationToken is the authentication token that is stored in the
    apple pass

    raises a 401 exception if the token is not correct
    """
    
    for pass_registration_handler in get_pass_data_acquisitions():
        if authorization is None:
            get_settings().get_logger().warn(
                "check_authorization_failure",
                authorization=authorization,
                pass_type_identifier=pass_type_identifier,
                serial_number=serial_number,
                reason="no token given",
                realm="fastapi",
            )
            raise HTTPException(status_code=401, detail="Unauthorized - no token give")
        token = authorization.split(" ")[1]
        check = await pass_registration_handler.check_authentication_token(
            pass_type_identifier, serial_number, token
        )
        if not check:
            get_settings().get_logger().warn(
                "check_authorization_failure",
                authorization=authorization,
                pass_type_identifier=pass_type_identifier,
                serial_number=serial_number,
                reason="wrong token",
                realm="fastapi",
            )
            raise HTTPException(status_code=401, detail="Unauthorized - wrong token")


@router.post(
    "/devices/{deviceLibraryIdentitfier}/registrations/{passTypeIdentifier}/{serialNumber}"
)
async def register_pass(
    request: Request,
    deviceLibraryIdentitfier: str,
    passTypeIdentifier: str,
    serialNumber: str,
    authorization: Annotated[str | None, Header()] = None,
    data: PushToken | None = None,
    *,
    settings: Settings = Depends(get_settings),
):
    """
    Registration: register a device to receive push notifications for a pass.

    see: https://developer.apple.com/documentation/walletpasses/register_a_pass_for_update_notifications

    URL: POST https://yourpasshost.example.com/v1/devices/{deviceLibraryIdentifier}/registrations/{passTypeIdentifier}/{serialNumber}
    HTTP-Methode: POST
    HTTP-PATH: /v1/devices/{deviceLibraryIdentifier}/registrations/{passTypeIdentifier}/{serialNumber}
    HTTP-Path-Parameters:
        * deviceLibraryIdentifier: str (required) A unique identifier you use to identify and authenticate the device.
        * passTypeIdentifier: str (required) The pass type identifier of the pass to register for update notifications. This value corresponds to the value of the passTypeIdentifier key of the pass.
        * serialNumber: str (required)
    HTTP-Headers:
        * Authorization: ApplePass <authenticationToken>
    HTTP-Body: JSON payload:
        * pushToken: <push token, which the server needs to send push notifications to this device> }

    Params definition
    :deviceLibraryIdentitfier      - the device's identifier
    :passTypeIdentifier   - the bundle identifier for a class of passes, sometimes referred to as the pass topic, e.g. pass.com.apple.backtoschoolgift, registered with WWDR
    :serialNumber  - the pass' serial number
    :pushToken      - the value needed for Apple Push Notification service

    server action: if the authentication token is correct, associate the given push token and device identifier with this pass
    server response:
    --> if registration succeeded: 201
    --> if this serial number was already registered for this device: 304
    --> if not authorized: 401

    :async:
    :param str deviceLibraryIdentifier: A unique identifier you use to identify and authenticate the device.
    :param str passTypeIdentifier:      The pass type identifier of the pass to register for update notifications. This value corresponds to the value of the passTypeIdentifier key of the pass.
    :param str serialNumber:            The serial number of the pass to register. This value corresponds to the serialNumber key of the pass.

    :return:
    """
    # TODO: auth handling

    logger = settings.get_logger()
    logger.info(
        "register_pass",
        deviceLibraryIdentitfier=deviceLibraryIdentitfier,
        passTypeIdentifier=passTypeIdentifier,
        serialNumber=serialNumber,
        authorization=authorization,
        realm="fastapi",
        url=request.url,
        push_token=data,
    )
    await check_authorization(authorization, passTypeIdentifier, serialNumber)



    for pass_registration_handler in get_pass_registrations():
        await pass_registration_handler.register_pass(
            deviceLibraryIdentitfier, passTypeIdentifier, serialNumber, data
        )


@router.delete(
    "/devices/{deviceLibraryIdentitfier}/registrations/{passTypeIdentifier}/{serialNumber}"
)
async def unregister_pass(
    request: Request,
    deviceLibraryIdentitfier: str,
    passTypeIdentifier: str,
    serialNumber: str,
    authorization: Annotated[str | None, Header()] = None,
    *,
    settings: Settings = Depends(get_settings),
):
    """
    Unregister

    unregister a device to receive push notifications for a pass

    DELETE /v1/devices/<deviceID>/registrations/<passTypeID>/<serial#>
    Header: Authorization: ApplePass <authenticationToken>

    server action: if the authentication token is correct, disassociate the device from this pass
    server response:
    --> if disassociation succeeded: 200
    --> if not authorized: 401

    """
    await check_authorization(authorization, passTypeIdentifier, serialNumber)

    logger = settings.get_logger()
    logger.info(
        "unregister_pass",
        deviceLibraryIdentitfier=deviceLibraryIdentitfier,
        passTypeIdentifier=passTypeIdentifier,
        serialNumber=serialNumber,
        realm="fastapi",
        url=request.url,
    )
    for pass_registration_handler in get_pass_registrations():
        await pass_registration_handler.unregister_pass(
            deviceLibraryIdentitfier, passTypeIdentifier, serialNumber
        )


@router.post("/log")
async def device_log(
    request: Request,
    data: LogEntries,
    *,
    settings: Settings = Depends(get_settings),
):
    """
    Logging/Debugging from the device, called by the handheld device

    log an error or unexpected server behavior, to help with server debugging
    POST /v1/log
    JSON payload: { "description" : <human-readable description of error> }

    server response: 200
    """
    for logging_handler in get_logging_handlers():
        await logging_handler.log(data)


@router.get("/download-pass/{token}")
async def download_pass(request: Request, token: str, settings=Depends(get_settings)):
    """
    download a pass from the server. The parameter is a token, so fromoutside
    the personal pass data are not deducible.

    GET /v1/download-pass/<token>

    server response:
    --> if token is correct: 200, with pass data payload as pkpass-file
    --> if token is incorrect: 401
    """
    logger = settings.get_logger()
    logger.info(
        "download_pass",
        realm="fastapi",
        url=request.url,
    )
    pass_type_identifier, serial_number = api.extract_auth_token(
        token, settings.fernet_key
    )
    res = await prepare_pass(pass_type_identifier, serial_number, update=False)

    fh = api.pkpass(res)

    headers = {
        "Content-Disposition": 'attachment; filename="blurb.pkpass"',
        "Content-Type": "application/octet-stream",
        "Last-Modified": f"{datetime.datetime.now()}",
    }

    return StreamingResponse(
        fh,
        headers=headers,
        media_type="application/vnd.apple.pkpass",
    )


@router.get("/passes/{passTypeIdentifier}/{serialNumber}")
async def get_updated_pass(
    request: Request,
    passTypeIdentifier: str,
    serialNumber: str,
    authorization: Annotated[str | None, Header()] = None,
    # *,
    settings: Settings = Depends(get_settings),
):
    """
    Pass delivery

    GET /v1/passes/<typeID>/<serial#>
    Header: Authorization: ApplePass <authenticationToken>

    server response:
    --> if auth token is correct: 200, with pass data payload as pkpass-file
    --> if auth token is incorrect: 401
    """

    await check_authorization(authorization, passTypeIdentifier, serialNumber)

    logger = settings.get_logger()
    logger.info(
        "get_updated_pass",
        passTypeIdentifier=passTypeIdentifier,
        serialNumber=serialNumber,
        realm="fastapi",
        url=request.url,
    )
    res = await prepare_pass(passTypeIdentifier, serialNumber, update=True)
    fh = api.pkpass(res)

    headers = {
        "Content-Disposition": 'attachment; filename="blurb.pkpass"',
        "Content-Type": "application/octet-stream",
        "Last-Modified": f"{datetime.datetime.now()}",
    }

    # Erstelle eine StreamingResponse mit dem BytesIO-Objekt
    return StreamingResponse(
        fh,
        headers=headers,
        media_type="application/vnd.apple.pkpass",
    )


async def prepare_pass(
    passTypeIdentifier: str, serialNumber: str, update: bool
) -> api.PkPass:
    """
    helper function to prepare a pass for delivery.
    it is used for initially dowloading a pass and for updating a pass.
    The latter endpoint is protected by an authentication token.

    this function retrieves an unsigned pass from the database, sets individual
    properties (teamIdetifier, passTypeIdentifier) and signs the pass.
    """
    for get_pass_data_acquisition_handler in get_pass_data_acquisitions():
        pass_data = await get_pass_data_acquisition_handler.get_pass_data(
            pass_type_id=passTypeIdentifier, serial_number=serialNumber, update=update
        )
        settings = Settings()
        # now we have to deserialize a PkPass, set individual propsand sign it
        pass1 = api.new(file=pass_data)
        pass1.pass_object_safe.teamIdentifier = settings.team_identifier
        # pass1.pass_object_safe.passTypeIdentifier = passTypeIdentifier
        # pass1.pass_object_safe.serialNumber = serialNumber

        scheme = "https"
        # chop off the last part of the path because it contains the
        # apple api version and this is automatically added by the the
        # device when it calls this endpoint
        apipath = "/".join(router.prefix.split("/")[:-1])
        weburl = f"{scheme}://{settings.domain}:{settings.https_port}{apipath}"
        pass1.pass_object_safe.webServiceURL = weburl
        # pass1.pass_object_safe.authenticationToken = None
        api.sign(pass1)

        return pass1


@router.get(
    "/devices/{deviceLibraryIdentifier}/registrations/{passTypeIdentifier}",
    response_model=SerialNumbers,
)
async def list_updatable_passes(
    request: Request,
    deviceLibraryIdentifier: str,
    passTypeIdentifier: str,
    passesUpdatedSince: str | None = None,
    *,
    settings: Settings = Depends(get_settings),
) -> SerialNumbers:
    """
    see https://developer.apple.com/documentation/walletpasses/get-the-list-of-updatable-passes

    Attention: check for correct authentication token, do not allow it to be called
    anonymously
    """
    logger = settings.get_logger()
    logger.info(
        "list_updatable_passes",
        deviceLibraryIdentifier=deviceLibraryIdentifier,
        passTypeIdentifier=passTypeIdentifier,
        passesUpdatedSince=passesUpdatedSince,
        realm="fastapi",
        url=request.url,
    )
    for pass_registration_handler in get_pass_data_acquisitions():
        serial_numbers = await pass_registration_handler.get_update_serial_numbers(
            deviceLibraryIdentifier, passTypeIdentifier, passesUpdatedSince
        )

        logger.info(
            "list_updatable_passes", realm="fastapi", serial_numbers=serial_numbers
        )
        return serial_numbers

    logger.info(
        "list_updatable_passes",
        realm="fastapi",
        serial_numbers=serial_numbers,
        empty=True,
    )
    return SerialNumbers(serialNumers=[], lastUpdated="")


@router.post("/passes/{passTypeIdentifier}/{serialNumber}")
async def update_pass(
    request: Request,
    passTypeIdentifier: str,
    serialNumber: str,
    authorization: Annotated[str | None, Header()] = None,
    *,
    settings: Settings = Depends(get_settings),
) -> list[PushToken]:
    """
    see https://developer.apple.com/documentation/walletpasses/update-a-pass

    Attention: check for correct authentication token, do not allow it to be called
    anonymously

    see https://developer.apple.com/documentation/UserNotifications/sending-notification-requests-to-apns

    for push notification handling
    """
    logger = settings.get_logger()
    logger.info(
        "update_pass",
        passTypeIdentifier=passTypeIdentifier,
        serialNumber=serialNumber,
        realm="fastapi",
        url=request.url,
    )
    # fetch the push tokens
    for handler in get_pass_data_acquisitions():
        push_tokens = await handler.get_push_tokens(
            None, passTypeIdentifier, serialNumber
        )

    ssl_context = ssl.create_default_context()
    ssl_context.load_cert_chain(
        certfile=settings.get_certificate_path(passTypeIdentifier),
        keyfile=settings.private_key,
    )

    updated = []

    # now call APN for each push-token
    for push_token in push_tokens:
        url = f"https://api.push.apple.com/3/device/{push_token.pushToken}"
        headers = {"apns-topic": passTypeIdentifier}

        logger.info(
            "update_pass", action="call APN", realm="fastapi", url=url, headers=headers
        )

        async with httpx.AsyncClient(http2=True, verify=ssl_context) as client:
            response = await client.post(
                url,
                headers=headers,
                json={},
            )

            if response.status_code == 200:
                updated.append(push_token)

    logger.info("update_pass", realm="fastapi", updated=updated)
    return updated
