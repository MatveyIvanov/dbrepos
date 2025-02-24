from typing import Type, TypeVar

from repo.core.exceptions import BaseRepoException

TObject = TypeVar("TObject")

BASE_EXCEPTION = BaseRepoException
BASE_MSG = "Not found."


def get_object_or_404(
    obj: TObject | None,
    *,
    msg: str | None = None,
    exc: Type[Exception] = BASE_EXCEPTION,
) -> TObject:
    """
    Similar to Django shortcut.
    If object is None, exception is raised.
    Otherwise object is returned.

    Args:
        obj (TObject | None): Object to return
        msg (str | None, optional): Message for exception.
            Defaults to None
        exc (Type[Exception]): Exception to raise.
            Defaults to BASE_EXCEPTION

    Raises:
        BASE_EXCEPTION: If object is None

    Returns:
        TObject: Final object
    """

    msg = msg if msg else BASE_MSG
    if obj is None:
        raise exc(msg)
    return obj
