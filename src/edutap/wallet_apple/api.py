from .models import passes
from typing import BinaryIO
from typing import Optional


def new(data: Optional[dict] = None, file: Optional[BinaryIO] = None) -> passes.PkPass:
    """
    Create pass model.

    :param data: JSON serializable dictionary.
    :param file: Binary IO data containing an existing PkPass file.
    :return: PkPass model instance.
    """
    ...
