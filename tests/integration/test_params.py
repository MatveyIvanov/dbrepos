import functools
from typing import Any, Callable, Literal, Set

import pytest

from repo.core.types import Extra, mode, operator
from tests.entities import TableEntity
from tests.integration.conftest import Runner
from tests.parametrize import (
    convert_to_parametrize,
    for_update_parametrize,
    include_soft_deleted_parametrize,
    methods_parametrize,
    multi_repo_parametrize,
    order_by_parametrize,
    session_parametrize,
    strict_parametrize,
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
METHOD_TO_QUERY_TYPE = {
    "create": "insert",
    "get_by_field": "select",
    "get_by_filters": "select",
    "get_by_pk": "select",
    "all": "select",
    "all_by_field": "select",
    "all_by_filters": "select",
    "all_by_pks": "select",
    "update": "update",
    "multi_update": "update",
    "delete": "delete",
    "delete_by_field": "delete",
    "exists_by_field": "select",
    "exists_by_filters": "select",
    "count_by_field": "select",
    "count_by_filters": "select",
}
INSERT_METHODS = {"create"}
QueryType = Literal["select", "insert", "update", "delete"]


def method_supports_param(method_name: str, param: str) -> bool:
    if method_name not in METHOD_TO_SUPPORTED_PARAMS:
        # In case of wrong method we return True to force test to fail
        return True

    return param in METHOD_TO_SUPPORTED_PARAMS[method_name]


def method_supports_query_type(method_name: str, query_type: QueryType) -> bool:
    if method_name not in METHOD_TO_QUERY_TYPE:
        # In case of wrong method we return True to force test to fail
        return True

    return query_type == METHOD_TO_QUERY_TYPE[method_name]


def skip_if_param_not_supported(
    func: Callable | None = None,
    *,
    param: str,
) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            method = kwargs.get("method", "unknown")
            if not method_supports_param(method, param):
                pytest.skip(f"Method `{method}` does not support `{param}` param.")

            return func(*args, **kwargs)

        return wrapper

    if func is None:
        return decorator

    return decorator(func)


def skip_if_query_type_not_supported(
    func: Callable | None = None,
    *,
    query_type: QueryType,
) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            method = kwargs.get("method", "unknown")
            if not method_supports_query_type(method, query_type):
                pytest.skip(
                    f"Method `{method}` does not support `{query_type}` query type."
                )

            return func(*args, **kwargs)

        return wrapper

    if func is None:
        return decorator

    return decorator(func)


def skip_runners(
    func: Callable | None = None,
    *,
    runners: Set[Runner],
    reason: str | None = None,
) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            runner = kwargs.get("runner", "unknown")
            if runner in runners:
                pytest.skip(
                    f"Runner `{runner}` skipped due to: {reason or 'no reason provided'}."
                )

            return func(*args, **kwargs)

        return wrapper

    if func is None:
        return decorator

    return decorator(func)


def skip_methods(
    func: Callable | None = None,
    *,
    methods: Set[str],
    reason: str | None = None,
) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            method = kwargs.get("method", "unknown")
            if method in methods:
                pytest.skip(
                    f"Method `{method}` skipped due to: {reason or 'no reason provided'}."
                )

            return func(*args, **kwargs)

        return wrapper

    if func is None:
        return decorator

    return decorator(func)


@pytest.mark.django_db
@pytest.mark.integration
@multi_repo_parametrize
@strict_parametrize
@methods_parametrize
@skip_if_param_not_supported(param="strict")
def test_strict_param(
    preload,
    specific_kwargs_override,
    strict,
    expected_preload_index,
    expected_error,
    repo,
    runner,
    method,
    specific_kwargs,
    return_type,
    insert,
    Filter,
    FilterSeq,
    request,
):
    repo = request.getfixturevalue(repo)

    for key, value in specific_kwargs.items():
        if key in specific_kwargs_override:
            specific_kwargs[key] = specific_kwargs_override[key]
    specific_kwargs.pop("strict", None)
    if "filters" in specific_kwargs:
        specific_kwargs["filters"] = FilterSeq(runner)(
            mode.and_,
            Filter(runner)(
                repo.table_class,
                "name",
                specific_kwargs_override["value"],
                operator.eq,
            ),
        )

    preload_ids = []
    for row in preload:
        preload_ids.append(insert("table", runner, row).id)

    if expected_error:
        with pytest.raises(expected_error):
            getattr(repo, method)(
                **specific_kwargs,
                strict=strict,
                convert_to=TableEntity,
            )
    else:
        result = getattr(repo, method)(
            **specific_kwargs,
            strict=strict,
            convert_to=TableEntity,
        )

        if expected_preload_index is not None:
            assert result is not None
            assert result.id == preload_ids[expected_preload_index]
        else:
            assert result is None


@pytest.mark.django_db
@pytest.mark.integration
@pytest.mark.xfail
@multi_repo_parametrize
@session_parametrize
@methods_parametrize
@skip_if_param_not_supported(param="session")
def test_session_param(
    repo,
    runner,
    session_factory,
    expect_usage,
    expect_for_runner,
    method,
    specific_kwargs,
    return_type,
    Filter,
    FilterSeq,
    request,
):
    # FIXME: nothing is really being tested here.
    # Its really hard to check session usage in integration test,
    # so checking it only in unit tests looks fine and may be considered
    repo = request.getfixturevalue(repo)
    if "filters" in specific_kwargs:
        specific_kwargs["filters"] = FilterSeq(runner)(
            mode.and_,
            Filter(runner)(repo.table_class, "name", "name", operator.eq),
        )

    if session_factory:
        with session_factory() as session:
            getattr(repo, method)(**specific_kwargs, session=session)

    else:
        getattr(repo, method)(**specific_kwargs, session=None)


@pytest.mark.django_db
@pytest.mark.integration
@multi_repo_parametrize
@convert_to_parametrize
@methods_parametrize
@skip_if_param_not_supported(param="convert_to")
def test_convert_to_param(
    repo,
    runner,
    convert_to,
    runner_to_expected_type,
    method,
    specific_kwargs,
    return_type,
    Filter,
    FilterSeq,
    insert,
    request,
):
    repo = request.getfixturevalue(repo)
    if "filters" in specific_kwargs:
        specific_kwargs["filters"] = FilterSeq(runner)(
            mode.and_,
            Filter(runner)(repo.table_class, "name", "name", operator.eq),
        )
    if method not in INSERT_METHODS:
        insert("table", runner, {"name": "name", "is_deleted": False})

    result = getattr(repo, method)(**specific_kwargs, convert_to=convert_to)

    if return_type == "instances":
        for item in result:
            assert isinstance(item, runner_to_expected_type[runner])
    else:
        assert isinstance(result, runner_to_expected_type[runner])


@pytest.mark.django_db
@pytest.mark.integration
@pytest.mark.xfail
@multi_repo_parametrize
@for_update_parametrize
@methods_parametrize
@skip_if_param_not_supported(param="extra")
@skip_if_query_type_not_supported(query_type="select")
@skip_runners(
    runners={"django"},
    reason="FIXME: not able to fetch queries for `FOR UPDATE` check",
)
def test_for_update_param(
    repo,
    runner,
    for_update,
    expect_lock,
    method,
    specific_kwargs,
    return_type,
    Filter,
    FilterSeq,
    insert,
    request,
):
    # FIXME: nothing is really being tested here.
    # Its really hard to check row locking in integration test,
    # so checking it only in unit tests looks fine and may be considered
    repo = request.getfixturevalue(repo)
    if "filters" in specific_kwargs:
        specific_kwargs["filters"] = FilterSeq(runner)(
            mode.and_,
            Filter(runner)(repo.table_class, "name", "name", operator.eq),
        )

    getattr(repo, method)(**specific_kwargs, extra=Extra(for_update=for_update))


@pytest.mark.django_db
@pytest.mark.integration
@pytest.mark.xfail
@multi_repo_parametrize
@include_soft_deleted_parametrize
@methods_parametrize
@skip_if_param_not_supported(param="extra")
def test_include_soft_deleted_param(
    repo,
    runner,
    preload,
    include_soft_deleted,
    expected_preload_indexes_by_repo_soft_deletable,
    expected_preload_indexes_overrides_by_method,
    method,
    specific_kwargs,
    return_type,
    Filter,
    FilterSeq,
    insert,
    select_one,
    request,
):
    repo = request.getfixturevalue(repo)
    if "filters" in specific_kwargs:
        specific_kwargs["filters"] = FilterSeq(runner)(
            mode.and_,
            Filter(runner)(repo.table_class, "name", "name", operator.eq),
        )
    if method_supports_param(method, "convert_to"):
        specific_kwargs["convert_to"] = TableEntity
    preload_ids = []
    for row in preload:
        preload_ids.append(insert("table", runner, row).id)

    result = getattr(repo, method)(
        **specific_kwargs,
        extra=Extra(include_soft_deleted=include_soft_deleted),
    )

    expected_preload_indexes = expected_preload_indexes_overrides_by_method.get(
        method, None
    )
    if expected_preload_indexes is None:
        expected_preload_indexes = expected_preload_indexes_by_repo_soft_deletable[
            repo.is_soft_deletable
        ]
    # This is trash, I know...
    # But this is an exception rather than a rule,
    # so just let it be here in shame...
    match return_type:
        case "null":
            match METHOD_TO_QUERY_TYPE[method]:
                case "update" | "multi_update":
                    for i, id_ in enumerate(preload_ids):
                        instance = select_one("table", id_, runner, TableEntity)
                        assert instance.name == (
                            specific_kwargs["values"]["name"]
                            if i
                            in (
                                expected_preload_indexes
                                if repo.is_soft_deletable or method != "update"
                                else expected_preload_indexes_by_repo_soft_deletable[
                                    False
                                ][:1]
                            )
                            else preload[0]["name"]
                        )
                case "delete" | "delete_by_field":
                    for i, id_ in enumerate(preload_ids):
                        instance = select_one("table", id_, runner, TableEntity)
                        if i in (
                            expected_preload_indexes
                            if repo.is_soft_deletable or method != "delete"
                            else expected_preload_indexes_by_repo_soft_deletable[False][
                                :1
                            ]
                        ):
                            assert instance is None
                        else:
                            assert instance is not None
                case _:
                    pytest.skip(
                        "Unexpected combination of query type "
                        f"`{METHOD_TO_QUERY_TYPE[method]}` and return type `null`."
                    )
        case "instance":
            if repo.is_soft_deletable and not expected_preload_indexes:
                assert result is None
            else:
                assert result is not None
                assert (
                    result.id == preload_ids[expected_preload_indexes[0]]
                    if repo.is_soft_deletable
                    else preload_ids[0]
                )
        case "instances":
            assert len(result) == (
                len(expected_preload_indexes)
                if repo.is_soft_deletable
                else len(preload)
            )
            preload_id = iter(preload_ids)
            for item, expected_preload_index in zip(result, expected_preload_indexes):
                assert item.id == (
                    preload_ids[expected_preload_index]
                    if repo.is_soft_deletable
                    else next(preload_id)
                )
        case "exists":
            assert result is bool(expected_preload_indexes)
        case "count":
            assert result == len(expected_preload_indexes)


@pytest.mark.django_db
@pytest.mark.integration
@pytest.mark.xfail
@multi_repo_parametrize
@order_by_parametrize
@methods_parametrize
@skip_if_param_not_supported(param="extra")
@skip_if_query_type_not_supported(query_type="select")
@skip_methods(
    methods={
        "get_by_pk",
        "exists_by_field",
        "exists_by_filters",
        "count_by_field",
        "count_by_filters",
    },
    reason="ordering param has no effect on this method.",
)
def test_order_by_param(
    repo,
    runner,
    preload,
    order_by,
    expected_preload_indexes,
    expected_preload_indexes_overrides,
    method,
    specific_kwargs,
    return_type,
    Filter,
    FilterSeq,
    insert,
    select_one,
    request,
):
    repo = request.getfixturevalue(repo)
    if "filters" in specific_kwargs:
        specific_kwargs["filters"] = FilterSeq(runner)(
            mode.and_,
            Filter(runner)(repo.table_class, "name", ["name", "a", "b"], operator.in_),
        )
    if method_supports_param(method, "convert_to"):
        specific_kwargs["convert_to"] = TableEntity
    preload_ids = []
    for row in preload:
        preload_ids.append(insert("table", runner, row).id)

    result = getattr(repo, method)(**specific_kwargs, extra=Extra(ordering=order_by))

    expected_preload_indexes = (
        expected_preload_indexes_overrides.get(method, None) or expected_preload_indexes
    )
    if return_type == "instance":
        assert result.id == preload_ids[expected_preload_indexes[0]]
    else:
        assert len(result) == len(expected_preload_indexes)
        for item, expected_index in zip(result, expected_preload_indexes):
            assert item.id == preload_ids[expected_index]


# NOTE: explanation for missing `select_related` params tests.
# First of all, Django - this is a perfect case for unit testing,
# as is really hard to do integration test in django for this types of
# orm usages.
# Secondly, SQLAlchemy - does not support this param yet.
# For now, it seems like integrational tests
# could be easily written with help of ORM events.
