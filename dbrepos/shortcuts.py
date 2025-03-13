from typing import Type, TypeVar

from dbrepos.core.exceptions import BaseRepoException

TObject = TypeVar("TObject")

BASE_MSG = "Not found."


def get_object_or_404(
    obj: TObject | None,
    *,
    msg: str | None = None,
    exc: Type[Exception] = BaseRepoException,
) -> TObject:
    """Strict object retrieval

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
        BaseRepoException: If object is None

    Returns:
        TObject: Final object
    """

    msg = msg if msg else BASE_MSG
    if obj is None:
        raise exc(msg)
    return obj
