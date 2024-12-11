from typing import Optional, BinaryIO


def new(
    data: Optional[dict]=None,
    file: Optional[BinaryIO]=None
):
    """
    Create pass model.

    :param data: JSON serializable dictionary.
    :param file: Binary IO data containing an existing PkPass file.
    :return: PkPass model instance.
    """
