from .models import passes
from .models.passes import PkPass  # noqa: F401
from edutap.wallet_apple.plugins import get_pass_data_acquisitions
from edutap.wallet_apple.settings import Settings
from typing import Any
from typing import BinaryIO
from typing import Optional

import cryptography.fernet
import httpx
import ssl


def new(
    data: Optional[dict[str, Any]] = None, file: Optional[BinaryIO] = None
) -> passes.PkPass:
    """
    Create pass model.

    :param data: JSON serializable dictionary.
    :param file: Binary IO data containing an existing PkPass zip file.
    :return: PkPass model instance.

    you must provide either data or file
    """
    if data is not None and file is not None:
        raise ValueError(
            "only either 'data' or 'file' may be provided, both is not allowed"
        )

    if data is not None:
        pass_object = passes.Pass.model_validate(data)
        pkpass = passes.PkPass.from_pass(pass_object)
    elif file is not None:
        pkpass = passes.PkPass.from_zip(file)
    else:
        pkpass = passes.PkPass()

    return pkpass


def verify(
    pkpass: passes.PkPass, recompute_manifest=True, settings: Settings | None = None
):
    """
    Verify the pass.

    :param pkpass: PkPass model instance.
    :return: True if the pass is valid, False otherwise.
    """
    pkpass.verify(recompute_manifest=recompute_manifest)


def sign(pkpass: passes.PkPass, settings: Settings | None = None):
    """
    Sign the pass.

    :param pkpass: PkPass model instance.
    :param settings: Settings model instance. if not given it will be loaded from the environment.
    works inplace, the pkpass will be signed.
    """
    if settings is None:
        settings = Settings()

    passtype_identifier = pkpass.pass_object_safe.passTypeIdentifier

    with open(settings.private_key, "rb") as fh:
        private_key_data = fh.read()
    with open(settings.get_certificate_path(passtype_identifier), "rb") as fh:
        certificate_data = fh.read()
    with open(settings.wwdr_certificate, "rb") as fh:
        wwdr_certificate_data = fh.read()

    pkpass.sign_direct(
        private_key_data,
        certificate_data,
        wwdr_certificate_data,
    )


def pkpass(pkpass: passes.PkPass) -> BinaryIO:
    """
    Save the pass to a file.

    :param pkpass: PkPass model instance.
    :param file: Binary IO file object.
    """
    pkpass._create_manifest()
    return pkpass.as_zip_bytesio()


def create_auth_token(
    pass_type_identifier: str, serial_number: str, fernet_key: str | bytes | None = None
) -> bytes:
    """
    create an authentication token using cryptography.Fernet symmetric encryption
    """
    if fernet_key is None:
        settings = Settings()
        assert settings.fernet_key, "fernet_key is not set in the settings"
        fernet_key = settings.fernet_key.encode("utf-8")

    if not isinstance(fernet_key, bytes):
        fernet_key = fernet_key.encode("utf-8")
    fernet = cryptography.fernet.Fernet(fernet_key)
    token = fernet.encrypt(f"{pass_type_identifier}:{serial_number}".encode())
    return token


def extract_auth_token(
    token: str | bytes, fernet_key: bytes | None = None
) -> tuple[str, str]:
    """
    extract the pass_type_identifier and serial_number from the authentication token
    """
    if fernet_key is None:
        settings = Settings()
        assert settings.fernet_key is not None, "fernet_key is not set in the settings"
        fernet_key = settings.fernet_key.encode("utf-8")

    if not isinstance(token, bytes):
        token = token.encode()
    fernet = cryptography.fernet.Fernet(fernet_key)
    decrypted = fernet.decrypt(token)
    pass_type_id, serial_number = decrypted.decode().split(":")
    return pass_type_id, serial_number


def save_link(
    pass_type_id: str,
    serial_number: str,
    settings: Settings | None = None,
    url_prefix: str | None = None,
    schema: str = "https",
) -> str:
    """
    creates a link to download the pass
    this link is encrypted, so that the pass holder identity
    cannot be inferred from the link

    :param identifier: Pass identifier.
    """
    if settings is None:
        settings = Settings()

    url_prefix = settings.handler_prefix
    if url_prefix[0] != "/":
        url_prefix = f"/{url_prefix}"

    token = create_auth_token(pass_type_id, serial_number, settings.fernet_key).decode(
        "utf-8"
    )
    if settings.https_port == 443 or not settings.https_port:
        return f"{schema}://{settings.domain}{url_prefix}/v1/download-pass/{token}"

    return f"{schema}://{settings.domain}:{settings.https_port}{url_prefix}/v1/download-pass/{token}"


async def trigger_update(
    passTypeIdentifier, serialNumber, settings: Settings | None = None
):
    """
    performs a APNs call to push an update to a pass/device
    """
    if settings is None:
        settings = Settings()

    logger = settings.get_logger()

    # fetch the push tokens
    for handler in get_pass_data_acquisitions():
        push_tokens = await handler.get_push_tokens(
            None, passTypeIdentifier, serialNumber
        )

    # create the ssl context for the APN call based on the certificate for the passTypeIdentifier
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
