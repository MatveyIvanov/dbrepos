import pytest

from repo.core.abstract import mode, operator
from tests.parametrize import (
    convert_to_parametrize,
    methods_parametrize,
    multi_repo_parametrize,
    session_parametrize,
)

# NOTE: inspect fails with overloaded methods,
# so its easier to check this way
METHOD_TO_SUPPORTED_PARAMS = {
    "create": {"entity", "session", "convert_to"},
    "get_by_field": {"name", "value", "strict", "extra", "session", "convert_to"},
    "get_by_filters": {"filters", "strict", "extra", "session", "convert_to"},
    "get_by_pk": {"pk", "strict", "extra", "session", "convert_to"},
    "all": {"extra", "session", "convert_to"},
    "all_by_field": {"name", "value", "extra", "session", "convert_to"},
    "all_by_filters": {"filters", "extra", "session", "convert_to"},
    "all_by_pks": {"pks", "extra", "session", "convert_to"},
    "update": {"pk", "values", "extra", "session"},
    "multi_update": {"pks", "values", "extra", "session"},
    "delete": {"pk", "values", "extra", "session"},
    "delete_by_field": {"name", "value", "extra", "session"},
    "exists_by_field": {"name", "value", "extra", "session"},
    "exists_by_filters": {"filters", "extra", "session"},
    "count_by_field": {"name", "value", "extra", "session"},
    "count_by_filters": {"filters", "extra", "session"},
}
INSERT_METHODS = {"create"}


def method_supports_param(method_name: str, param: str) -> bool:
    if method_name not in METHOD_TO_SUPPORTED_PARAMS:
        # In case of wrong method we return True to force test to fail
        return True

    return param in METHOD_TO_SUPPORTED_PARAMS[method_name]


@pytest.mark.django_db
@pytest.mark.integration
@multi_repo_parametrize
@session_parametrize
@methods_parametrize
def test_session_param(
    repo,
    runner,
    session_factory,
    expect_usage,
    expect_for_runner,
    check_session_usage,
    method,
    specific_kwargs,
    returns_many,
    Filter,
    FilterSeq,
    request,
):
    if not method_supports_param(method, "session"):
        pytest.skip(f"Method `{method}` does not support `session` param.")

    repo = request.getfixturevalue(repo)
    if "filters" in specific_kwargs:
        specific_kwargs["filters"] = FilterSeq(runner)(
            mode.and_,
            Filter(runner)(repo.table_class, "name", "name", operator.eq),
        )

    if session_factory:
        with session_factory() as session:
            check_session_usage(session, runner, expect_usage, expect_for_runner)

            getattr(repo, method)(**specific_kwargs, session=session)

    else:
        getattr(repo, method)(**specific_kwargs, session=None)


@pytest.mark.django_db
@pytest.mark.integration
@multi_repo_parametrize
@convert_to_parametrize
@methods_parametrize
def test_convert_to_param(
    repo,
    runner,
    convert_to,
    runner_to_expected_type,
    method,
    specific_kwargs,
    returns_many,
    Filter,
    FilterSeq,
    insert,
    request,
):
    if not method_supports_param(method, "convert_to"):
        pytest.skip(f"Method `{method}` does not support `convert_to` param.")

    repo = request.getfixturevalue(repo)
    if "filters" in specific_kwargs:
        specific_kwargs["filters"] = FilterSeq(runner)(
            mode.and_,
            Filter(runner)(repo.table_class, "name", "name", operator.eq),
        )
    if method not in INSERT_METHODS:
        insert("table", runner, {"name": "name", "is_deleted": False})

    result = getattr(repo, method)(**specific_kwargs, convert_to=convert_to)

    if returns_many:
        for item in result:
            assert isinstance(item, runner_to_expected_type[runner])
    else:
        assert isinstance(result, runner_to_expected_type[runner])
