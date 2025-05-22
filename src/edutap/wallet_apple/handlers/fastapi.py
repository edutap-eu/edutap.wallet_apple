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
from starlette.status import HTTP_200_OK
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN,
from fastapi import Request
from fastapi.responses import StreamingResponse
from typing import Annotated

import datetime


settings = Settings()

# define routers for all use cases: wallet_web_service (update service), pass_download requested by Wallet
# and the combined router (at bottom of file)

# router that handles the Apple Wallet Web Service API (Update Service of Passes)
# handling the following endpoints:
#   POST register pass: https://yourpasshost.example.com/v1//devices/{deviceLibraryIdentifier}/registrations/{passTypeIdentifier}/{serialNumber}
#   DELETE unregister pass: https://yourpasshost.example.com/v1//devices/{deviceLibraryIdentifier}/registrations/{passTypeIdentifier}/{serialNumber}
#   GET get_updated_pass https://yourpasshost.example.com/v1//passes/{passTypeIdentifier}/{serialNumber}
#   GET list_updatable_passes: https://yourpasshost.example.com/v1//devices/{deviceLibraryIdentifier}/registrations/{passTypeIdentifier}
#   POST logging info issued by handheld: https://yourpasshost.example.com/v1//log
router_webservice = APIRouter(
    prefix=settings.handler_prefix_webservice,
    tags=["edutap.wallet_apple"],
)
router_apple_wallet = router_webservice  # backward compatibility alias

# router that handles the pass download request from the Wallet app
# (e.g. when the user request a loyalty card from with the Wallet --> Loyalty onboarding process)
# handling the following endpoints:
#   POST https://yourpasshost.example.com/v1/passes/{passTypeIdentifier}/{serialNumber}/personalize
router_wallet_requested_pass_download = APIRouter(
    prefix=settings.handler_prefix_wallet_requested_pass_download,
    tags=["edutap.wallet_apple"],
)
router_download_pass = router_wallet_requested_pass_download  # backward compatibility alias


def get_prefix() -> str:
    prefix = f"{settings.handler_prefix}/v1"
    if prefix[0] != "/":
        prefix = f"/{prefix}"
    return prefix


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

    # check if the token is present
    if authorization is None:
        settings.get_logger().warn(
            "check_authorization_failure",
            authorization=authorization,
            pass_type_identifier=pass_type_identifier,
            serial_number=serial_number,
            reason="no token given",
            realm="fastapi",
        )
        if settings.env in ["development", "testing"]:
            # in development and testing mode, we pass additional information
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="UNAUTHORIZED - no token given",
            )
        raise HTTPException(status_code=401, detail="UNAUTHORIZED")

    auth_type, token = authorization.split(" ")
    if auth_type != "ApplePass":
        settings.get_logger().warn(
            "check_authorization_failure",
            authorization=authorization,
            pass_type_identifier=pass_type_identifier,
            serial_number=serial_number,
            reason="wrong token type",
            realm="fastapi",
        )

        if settings.env in ["development", "testing"]:
            # in development and testing mode, we pass additional information
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="UNAUTHORIZED - Not Supported Authentication Type",
            )
        raise HTTPException(status_code=401, detail="UNAUTHORIZED")
    for pass_registration_handler in get_pass_data_acquisitions():
        check = await pass_registration_handler.check_authentication_token(
            pass_type_identifier, serial_number, token
        )
        if not check:
            settings.get_logger().warn(
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
        pass1 = api.new(file=pass_data)
        pass1.pass_object_safe.teamIdentifier = settings.team_identifier
        # pass1.pass_object_safe.passTypeIdentifier = passTypeIdentifier
        # pass1.pass_object_safe.serialNumber = serialNumber

        scheme = "https"
        # chop off the last part of the path because it contains the
        # apple api version and this is automatically added by the the
        # device when it calls this endpoint
        apipath = "/".join(router_apple_wallet.prefix.split("/")[:-1])
        weburl = f"{scheme}://{settings.domain}:{settings.https_port}{apipath}"
        pass1.pass_object_safe.webServiceURL = weburl
        # pass1.pass_object_safe.authenticationToken = None
        api.sign(pass1)

        return pass1

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
        pass_type_identifier, serial_number = api.extract_auth_token(
            token, settings.fernet_key
        )
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
