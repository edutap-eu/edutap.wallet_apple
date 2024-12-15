from edutap.wallet_apple import crypto
from edutap.wallet_apple.settings import Settings
from .models import passes
from typing import Any, BinaryIO
from typing import Optional


def new(data: Optional[dict[str, Any]] = None, file: Optional[BinaryIO] = None) -> passes.PkPass:
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
        pass_object = passes.Pass.model_validate_json(data)
        pkpass = passes.PkPass.from_pass(pass_object)
    elif file is not None:
        pkpass = passes.PkPass.from_zip(file)
    else:
        pkpass = passes.PkPass()
    
    return pkpass


def verify(pkpass: passes.PkPass,recompute_manifest=True, settings: Settings|None=None):
    """
    Verify the pass.

    :param pkpass: PkPass model instance.
    :return: True if the pass is valid, False otherwise.
    """
    pkpass.verify(recompute_manifest=recompute_manifest)


def sign(pkpass: passes.PkPass, settings: Settings|None):
    """
    Sign the pass.

    :param pkpass: PkPass model instance.
    :param settings: Settings model instance. if not given it will be loaded from the environment.
    works inplace, the pkpass will be signed.
    """
    if settings is None:
        settings = Settings()

    pkpass.sign(settings.private_key, settings.certificate, settings.wwdr_certificate)
