from ..settings import Settings
from edutap.wallet_apple import api
from edutap.wallet_apple.models.handlers import LogEntries
from edutap.wallet_apple.models.handlers import PushToken
from edutap.wallet_apple.models.handlers import SerialNumbers
from edutap.wallet_apple.plugins import get_logging_handlers
from edutap.wallet_apple.plugins import get_pass_data_acquisitions
from edutap.wallet_apple.plugins import get_pass_registrations
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Header
from fastapi import HTTPException
from fastapi import Request
from fastapi.responses import StreamingResponse
from typing import Annotated

import datetime


def get_settings() -> Settings:
    res = Settings()
    return res


def get_prefix() -> str:
    prefix = f"{get_settings().handler_prefix}/v1"
    if prefix[0] != "/":
        prefix = f"/{prefix}"
    return prefix


# router that handles the apple wallet api:
#   POST register pass: /devices/{deviceLibraryIdentifier}/registrations/{passTypeIdentifier}/{serialNumber}
#   DELETE unregister pass: /devices/{deviceLibraryIdentifier}/registrations/{passTypeIdentifier}/{serialNumber}
#   GET get_updated_pass /passes/{passTypeIdentifier}/{serialNumber}
#   GET list_updatable_passes: /devices/{deviceLibraryIdentifier}/registrations/{passTypeIdentifier}
#   POST logging info issued by handheld: /log
router_apple_wallet = APIRouter(
    prefix=get_prefix(),
    tags=["edutap.wallet_apple"],
)

# download pass: /download-pass/{token}
router_download_pass = APIRouter(
    prefix=get_prefix(),
    tags=["edutap.wallet_apple"],
)


async def check_authorization(
    authorization: str | None,
    pass_type_identifier: str | None = None,
    serial_number: str | None = None,
) -> None:
    """
    check the authorization token as it comes in the request header for
    `register_pass`, `unregister_pass` and `get_pass` endpoints
    the authorization string is of the form `ApplePass <authenticationToken>`
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


@router_apple_wallet.post(
    "/devices/{deviceLibraryIdentifier}/registrations/{passTypeIdentifier}/{serialNumber}"
)
async def register_pass(
    request: Request,
    deviceLibraryIdentifier: str,
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
    :deviceLibraryIdentifier      - the device's identifier
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

    logger = settings.get_logger()
    logger.info(
        "register_pass",
        deviceLibraryIdentifier=deviceLibraryIdentifier,
        passTypeIdentifier=passTypeIdentifier,
        serialNumber=serialNumber,
        authorization=authorization,
        realm="fastapi",
        url=request.url,
        push_token=data,
    )
    await check_authorization(authorization, passTypeIdentifier, serialNumber)

    try:
        for pass_registration_handler in get_pass_registrations():
            await pass_registration_handler.register_pass(
                deviceLibraryIdentifier, passTypeIdentifier, serialNumber, data
            )
    except Exception as e:
        logger.error(
            "register_pass",
            deviceLibraryIdentifier=deviceLibraryIdentifier,
            passTypeIdentifier=passTypeIdentifier,
            serialNumber=serialNumber,
            authorization=authorization,
            realm="fastapi",
            url=request.url,
            push_token=data,
            error=str(e),
        )

        raise

    logger.info(
        "register_pass done",
        deviceLibraryIdentifier=deviceLibraryIdentifier,
        passTypeIdentifier=passTypeIdentifier,
        serialNumber=serialNumber,
        authorization=authorization,
        realm="fastapi",
        url=request.url,
        push_token=data,
    )


@router_apple_wallet.delete(
    "/devices/{deviceLibraryIdentifier}/registrations/{passTypeIdentifier}/{serialNumber}"
)
async def unregister_pass(
    request: Request,
    deviceLibraryIdentifier: str,
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
        deviceLibraryIdentifier=deviceLibraryIdentifier,
        passTypeIdentifier=passTypeIdentifier,
        serialNumber=serialNumber,
        realm="fastapi",
        url=request.url,
    )
    try:
        for pass_registration_handler in get_pass_registrations():
            await pass_registration_handler.unregister_pass(
                deviceLibraryIdentifier, passTypeIdentifier, serialNumber
            )
    except Exception as e:
        logger.error(
            "unregister_pass",
            deviceLibraryIdentifier=deviceLibraryIdentifier,
            passTypeIdentifier=passTypeIdentifier,
            serialNumber=serialNumber,
            authorization=authorization,
            realm="fastapi",
            url=request.url,
            error=str(e),
        )

        raise


@router_apple_wallet.post("/log")
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


@router_apple_wallet.get("/passes/{passTypeIdentifier}/{serialNumber}")
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

    try:
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
    except Exception as e:
        logger.error(
            "get_updated_pass",
            passTypeIdentifier=passTypeIdentifier,
            serialNumber=serialNumber,
            authorization=authorization,
            realm="fastapi",
            url=request.url,
            error=str(e),
        )

        raise


async def prepare_pass(
    passTypeIdentifier: str, serialNumber: str, update: bool
) -> api.PkPass:
    """
    helper function to prepare a pass for delivery.
    it is used for initially downloading a pass and for updating a pass.
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
        pkpass = api.new(file=pass_data)
        if settings.pass_data_passthrough:
            return pkpass
        pkpass.pass_object_safe.teamIdentifier = settings.team_identifier

        # chop off the last part of the path because it contains the
        # apple api version and this is automatically added by the the
        # device when it calls this endpoint
        apipath = "/".join(router_apple_wallet.prefix.split("/")[:-1])
        weburl = f"https://{settings.domain}:{settings.https_port}{apipath}"
        pkpass.pass_object_safe.webServiceURL = weburl
        await api.sign(pkpass)

        return pkpass

    raise LookupError("Pass not found")


@router_apple_wallet.get(
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

    try:
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
        return SerialNumbers(serialNumbers=[], lastUpdated="")
    except Exception as e:
        logger.error(
            "list_updatable_passes",
            deviceLibraryIdentifier=deviceLibraryIdentifier,
            passTypeIdentifier=passTypeIdentifier,
            passesUpdatedSince=passesUpdatedSince,
            realm="fastapi",
            url=request.url,
            error=str(e),
        )

        raise


@router_download_pass.get("/download-pass/{token}")
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

    try:
        pass_type_identifier, serial_number = api.extract_auth_token(token)
        res = await prepare_pass(pass_type_identifier, serial_number, update=False)

        fh = api.pkpass(res)

        headers = {
            "Content-Disposition": f'attachment; filename="{serial_number}.pkpass"',
            "Content-Type": "application/octet-stream",
            "Last-Modified": f"{datetime.datetime.now()}",
        }

        return StreamingResponse(
            fh,
            headers=headers,
            media_type="application/vnd.apple.pkpass",
        )
    except Exception as e:
        logger.error(
            "download_pass",
            realm="fastapi",
            url=request.url,
            error=str(e),
        )

        raise
