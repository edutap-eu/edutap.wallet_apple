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