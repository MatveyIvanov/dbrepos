import pytest

from dbrepos.core.types import mode, operator
from tests.parametrize import multi_repo_parametrize


@pytest.mark.django_db
@pytest.mark.integration
@multi_repo_parametrize
@pytest.mark.parametrize(
    "preload,name,value,operator_,expected_result",
    (
        ([], "name", "name", operator.eq, False),
        (
            [{"name": "name", "is_deleted": False}],
            "name",
            "unknown",
            operator.eq,
            False,
        ),
        ([{"name": "name", "is_deleted": False}], "name", "name", operator.eq, True),
        (
            [
                {"name": "name1", "is_deleted": False},
                {"name": "name2", "is_deleted": False},
            ],
            "name",
            "name1",
            operator.eq,
            True,
        ),
        (
            [
                {"name": "name1", "is_deleted": False},
                {"name": "name2", "is_deleted": False},
            ],
            "is_deleted",
            False,
            operator.is_,
            True,
        ),
    ),
)
def test_exists_by_filters(
    preload,
    name,
    value,
    operator_,
    expected_result,
    repo,
    runner,
    insert,
    Filter,
    FilterSeq,
    request,
):
    repo = request.getfixturevalue(repo)
    filters = FilterSeq(runner)(
        mode.and_,
        Filter(runner)(repo.table_class, name, value, operator_),
    )

    assert repo.exists_by_filters(filters=filters) is False

    for row in preload:
        insert("table", runner, row)

    assert repo.exists_by_filters(filters=filters) is expected_result
