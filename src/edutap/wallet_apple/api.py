import cryptography.fernet
from .models import passes
from .models.passes import PkPass

from edutap.wallet_apple.settings import Settings
from typing import Any
from typing import BinaryIO
from typing import Optional


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

    pkpass.sign(
        settings.private_key,
        settings.get_certificate_path(passtype_identifier),
        settings.wwdr_certificate,
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
    pass_type_identifier: str, serial_number: str, fernet_key: str | None = None
) -> str:
    """
    create an authentication token using cryptography.Fernet symmetric encryption
    """
    if fernet_key is None:
        settings = Settings()
        fernet_key = settings.fernet_key.encode("utf-8")

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
        fernet_key = settings.fernet_key.encode("utf-8")

    if not isinstance(token, bytes):
        token = token.encode()
    fernet = cryptography.fernet.Fernet(fernet_key)
    decrypted = fernet.decrypt(token)
    return decrypted.decode().split(":")


def save_link(
    pass_type_id: str,
    serial_number: str,
    settings: Settings | None = None,
    url_prefix: str = "/apple_update_service/v1",
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

    token = create_auth_token(pass_type_id, serial_number, settings.fernet_key).decode(
        "utf-8"
    )
    if settings.https_port == 443 or not settings.https_port:
        return f"{schema}://{settings.domain}{url_prefix}/download-pass/{token}"
    
    return f"{schema}://{settings.domain}:{settings.https_port}{url_prefix}/download-pass/{token}"
