from ..settings import AppleWalletSettings, Settings
from edutap.wallet_apple.models.handlers import LogEntries
from edutap.wallet_apple.models.handlers import PushToken
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Header
from fastapi import Request
from fastapi.concurrency import asynccontextmanager
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
    # *,
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

    raise NotImplementedError


@router.delete(
    "/devices/{deviceLibraryIdentitfier}/registrations/{passTypeIdentifier}/{serialNumber}"
)
async def unregister_pass(
    request: Request,
    deviceLibraryIdentitfier: str,
    passTypeIdentifier: str,
    serialNumber: str,
    authorization: Annotated[str | None, Header()] = None,
    # *,
    settings: AppleWalletSettings = Depends(get_settings),
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
    raise NotImplementedError


@router.post("/log")
async def device_log(
    request: Request,
    data: LogEntries,
    # *,
    # settings: AppleWalletSettings = Depends(get_settings),
):
    """
    Logging/Debugging from the device, called by the handheld device

    log an error or unexpected server behavior, to help with server debugging
    POST /v1/log
    JSON payload: { "description" : <human-readable description of error> }

    server response: 200
    """
    raise NotImplementedError


@router.get("/passes/{passTypeIdentifier}/{serialNumber}")
async def get_pass(
    request: Request,
    passTypeIdentifier: str,
    serialNumber: str,
    authorization: Annotated[str | None, Header()] = None,
    # *,
    settings: AppleWalletSettings = Depends(get_settings),
):
    """
    Pass delivery

    GET /v1/passes/<typeID>/<serial#>
    Header: Authorization: ApplePass <authenticationToken>

    server response:
    --> if auth token is correct: 200, with pass data payload as pkpass-file
    --> if auth token is incorrect: 401
    """
    raise NotImplementedError


# ------------------------
# Neuland
# ------------------------


@router.get(
    "/devices/{deviceLibraryIdentifier}/registrations/{passTypeIdentifier}?passesUpdatedSince={previousLastUpdated}"
)
async def list_updatable_passes(
    request: Request,
    deviceLibraryIdentifier: str,
    passTypeIdentifier: str,
    previousLastUpdated: str,
    authorization: Annotated[str | None, Header()] = None,
    # *,
    settings: AppleWalletSettings = Depends(get_settings),
):
    """
    not covered by Apple's documentation, so it is a custom implementation

    Attention: check for correct authentication token, do not allow it to be called
    anonymously
    """
