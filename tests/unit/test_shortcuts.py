import pytest

from dbrepos.core.exceptions import BaseRepoException
from dbrepos.shortcuts import BASE_MSG, get_object_or_404


class CustomException(BaseRepoException):
    pass


@pytest.mark.unit
@pytest.mark.parametrize(
    "obj,expected_exception",
    ((None, BaseRepoException), ({}, None)),
)
@pytest.mark.parametrize("msg", (None, "Custom message"))
@pytest.mark.parametrize("exc", (None, CustomException))
def test_get_object_or_404(exc, msg, obj, expected_exception):
    kwargs = {"obj": obj, "msg": msg}
    if exc is not None:
        kwargs["exc"] = exc

    if expected_exception is not None:
        with pytest.raises(expected_exception) as exc:
            get_object_or_404(**kwargs)
        assert str(exc.value) == (msg or BASE_MSG)
    else:
        assert get_object_or_404(**kwargs) == obj
