import datetime
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
from fastapi import Request
from fastapi.concurrency import asynccontextmanager
from fastapi.responses import StreamingResponse
from typing import Annotated


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


def check_authentification_token(
    authorization_header_string: str | None, auth_required: bool = True
) -> bool:
    raise NotImplementedError


# @router.get("/devices/{deviceLibraryIdentitfier}/registrations/{passTypeIdentifier}")
# async def list_registered_passes(
#     request: Request,
#     deviceLibraryIdentitfier: str,
#     passTypeIdentifier: str,
#     authorization: Annotated[str | None, Header()] = None,
#     *,
#     settings: Settings = Depends(get_settings),
# ):
#     """
#     List the serial numbers of passes registered for a device.

#     see: https://developer.apple.com/documentation/walletpasses/list_the_serial_numbers_of_passes_registered_for_a_device

#     URL: GET https://yourpasshost.example.com/v1/devices/{deviceLibraryIdentifier}/registrations/{passTypeIdentifier}
#     HTTP-Methode: GET
#     HTTP-PATH: /v1/devices/{deviceLibraryIdentifier}/registrations/{passTypeIdentifier}
#     HTTP-Path-Parameters:
#         * deviceLibraryIdentifier: str (required) A unique identifier you use to identify and authenticate the device.
#         * passTypeIdentifier: str (required) The pass type identifier of the passes to return. This value corresponds to the value of the passTypeIdentifier key of the passes.
#     HTTP-Headers:
#         * Authorization: ApplePass <authenticationToken>

#     Params definition
#     :deviceLibraryIdentitfier      - the device's identifier
#     :passTypeIdentifier   - the bundle identifier for a class of passes, sometimes referred to as the pass topic, e.g. pass.com.apple.backtoschoolgift, registered with WWDR

#     server action: if the authentication token is correct, return a list of serial numbers for passes associated with the device
#     server response:
#     --> if auth token is correct: 200, with a JSON payload containing an array of serial numbers
#     --> if auth token is incorrect: 401

#     :async:
#     :param str deviceLibraryIdentifier: A unique identifier you use to identify and authenticate the device.
#     :param str passTypeIdentifier:      The pass type identifier of the passes to return. This value corresponds to the value of the passTypeIdentifier key of the passes.

#     :return:
#     """
#     for pass_registration_handler in get_pass_registrations():
#         await pass_registration_handler.register_pass(
#             deviceLibraryIdentitfier, passTypeIdentifier, serialNumber, data
#         )


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


@router.get("/passes/{passTypeIdentifier}/{serialNumber}")
async def get_pass(
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

    # TODO: how shall we here handle more than one handler?
    # does that make sense when we return stuff?
    # TODO: auth handling

    for get_pass_data_acquisition_handler in get_pass_data_acquisitions():
        pass_data = await get_pass_data_acquisition_handler.get_pass_data(serialNumber)
        settings = Settings()
        # now we have to deserialize a PkPass object and sign it
        pass1 = api.new(file=pass_data)
        pass1.pass_object_safe.teamIdentifier = settings.team_identifier
        pass1.pass_object_safe.passTypeIdentifier = settings.pass_type_identifier
        pass1.pass_object_safe.description = f"created at: {datetime.datetime.now()}"
        # compute pass web url
        url = request.url
        newpath = "/".join(url.path.split("/")[:-4])
        scheme = url.scheme
        # scheme = "https" # only https is allowed, with a web url of type http the pass does not get accepted
        weburl = scheme + "://" + url.netloc + newpath
        # if scheme == "http":
        #     logger.error("Web URL is http, pass will not be accepted by Apple Wallet")

        scheme = "https"
        weburl = f"{scheme}://{settings.domain}:{settings.https_port}{newpath}"
        pass1.pass_object_safe.webServiceURL = weburl
        # pass1.pass_object_safe.authenticationToken = None

        api.sign(pass1)
        fh = api.pkpass(pass1)
        headers = {
            "Content-Disposition": 'attachment; filename="blurb.pkpass"',
            "Content-Type": "application/octet-stream",
        }

        # Erstelle eine StreamingResponse mit dem BytesIO-Objekt
        return StreamingResponse(
            fh,
            headers=headers,
            media_type="application/vnd.apple.pkpass",
        )


# ------------------------
# Neuland
# ------------------------


@router.get("/devices/{deviceLibraryIdentifier}/registrations/{passTypeIdentifier}")
async def list_updatable_passes(
    request: Request,
    deviceLibraryIdentifier: str,
    passTypeIdentifier: str,
    passesUpdatedSince: str,
    authorization: Annotated[str | None, Header()] = None,
    *,
    settings: Settings = Depends(get_settings),
) -> SerialNumbers:
    """
    see https://developer.apple.com/documentation/walletpasses/get-the-list-of-updatable-passes

    Attention: check for correct authentication token, do not allow it to be called
    anonymously
    """

    for pass_registration_handler in get_pass_data_acquisitions():
        serial_numbers = await pass_registration_handler.get_update_serial_numbers(
            deviceLibraryIdentifier, passTypeIdentifier, passesUpdatedSince
        )

        return serial_numbers

    return SerialNumbers(serialNumers=[], lastUpdated="")
