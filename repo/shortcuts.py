from typing import Type, TypeVar


TObject = TypeVar("TObject")

BASE_EXCEPTION = Exception
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

    Raises:
        BASE_EXCEPTION: If object is None

    Returns:
        TObject: Final object
    """

    msg = msg if msg else BASE_MSG
    if obj is None:
        raise exc(msg)
    return obj
