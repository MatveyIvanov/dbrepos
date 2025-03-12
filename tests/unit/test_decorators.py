import inspect
from unittest import mock

import pytest

from repository.core.exceptions import BaseRepoException
from repository.decorators import convert, handle_error, session, strict
from tests.entities import TableEntity


class CustomRepoException(BaseRepoException):
    pass


obj = dict()


@pytest.mark.unit
@pytest.mark.parametrize(
    "result,strict_,expected_result",
    (
        (obj, False, obj),
        (obj, True, obj),
        (BaseRepoException, False, None),
        (BaseRepoException, True, BaseRepoException),
        (CustomRepoException, False, None),
        (CustomRepoException, True, CustomRepoException),
    ),
)
def test_strict(result, strict_, expected_result):
    func = mock.Mock()
    is_class = inspect.isclass(result)

    if strict_ and is_class and issubclass(result, BaseRepoException):
        func.side_effect = result
        with pytest.raises(expected_result):
            strict(func)(strict=strict_)
    else:
        if is_class and issubclass(result, BaseRepoException):
            func.side_effect = result
        else:
            func.return_value = result
        assert strict(func)(strict=strict_) == expected_result

    func.assert_called_once()


@pytest.mark.unit
@pytest.mark.parametrize(
    "return_value,side_effect,exceptions,expected_exception",
    (
        (obj, None, (Exception,), None),
        (None, Exception, (Exception,), Exception),
        (None, BaseRepoException, (Exception,), BaseRepoException),
        (None, Exception, (BaseRepoException,), Exception),
    ),
)
def test_handle_error(return_value, side_effect, exceptions, expected_exception):
    func, logger = (
        mock.Mock(return_value=return_value, side_effect=side_effect),
        mock.Mock(),
    )

    if expected_exception is not None:
        with pytest.raises(expected_exception) as exc:
            handle_error(func, logger=logger, exceptions=exceptions)()

        logger.debug.assert_called_once_with(str(exc.value))
        if issubclass(side_effect, exceptions):
            logger.error.assert_called_once_with(
                f"Expected error - {exc.value}",
                exc_info=exc.value,
            )
        else:
            logger.critical.assert_called_once_with(
                f"Unexpected error - {exc.value}",
                exc_info=exc.value,
            )
    else:
        handle_error(func, logger=logger, exceptions=exceptions)()
        logger.debug.assert_not_called()
        logger.error.assert_not_called()

    func.assert_called_once()


@pytest.mark.unit
@pytest.mark.parametrize(
    "session_factory,expected_error",
    ((None, BaseRepoException), ("session_factory_mock", None)),
)
@pytest.mark.parametrize(
    "session_,expect_internal",
    ((None, True), ("session_mock", False)),
)
def test_session(
    session_,
    expect_internal,
    session_factory,
    expected_error,
    internal_session_mock,
    request,
):
    session_, session_factory = (
        request.getfixturevalue(session_) if session_ else session_,
        (
            request.getfixturevalue(session_factory)
            if session_factory
            else session_factory
        ),
    )
    repo = mock.Mock()
    func = mock.Mock()
    repo.session_factory = session_factory
    repo.func = func

    if expected_error:
        with pytest.raises(expected_error):
            session(repo.func)(repo, session=session_)
        func.assert_not_called()
    else:
        session(repo.func)(repo, session=session_)
        func.assert_called_once()
        if expect_internal:
            func.assert_called_with(repo, session=internal_session_mock)
        else:
            func.assert_called_with(repo, session=session_)


@pytest.mark.unit
@pytest.mark.parametrize(
    "many,orm,convert_to,result,expected_result",
    (
        (False, "alchemy", None, [(1, "name", False)], (1, "name", False)),
        (False, "alchemy", None, (1, "name", False), (1, "name", False)),
        (True, "alchemy", None, [(1, "name", False)], [(1, "name", False)]),
        (
            False,
            "alchemy",
            TableEntity,
            [(1, "name", False)],
            TableEntity(1, "name", False),
        ),
        (
            False,
            "alchemy",
            TableEntity,
            (1, "name", False),
            TableEntity(1, "name", False),
        ),
        (
            True,
            "alchemy",
            TableEntity,
            [(1, "name", False)],
            [TableEntity(1, "name", False)],
        ),
        (False, "django", None, (1, "name", False), (1, "name", False)),
        (True, "django", None, [(1, "name", False)], [(1, "name", False)]),
        (
            False,
            "django",
            TableEntity,
            [(1, "name", False)],
            TableEntity(1, "name", False),
        ),
        (
            False,
            "django",
            TableEntity,
            (1, "name", False),
            TableEntity(1, "name", False),
        ),
        (
            True,
            "django",
            TableEntity,
            [(1, "name", False)],
            [TableEntity(1, "name", False)],
        ),
    ),
)
def test_convert(many, orm, convert_to, result, expected_result):
    func = mock.Mock(return_value=result)

    assert convert(func, many=many, orm=orm)(convert_to=convert_to) == expected_result
