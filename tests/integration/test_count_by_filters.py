import pytest

from repository.core.types import mode, operator
from tests.parametrize import multi_repo_parametrize


@pytest.mark.django_db
@pytest.mark.integration
@multi_repo_parametrize
@pytest.mark.parametrize(
    "preload,name,value,operator_,expected_result",
    (
        ([], "name", "name", operator.eq, 0),
        ([{"name": "name", "is_deleted": False}], "name", "unknown", operator.eq, 0),
        ([{"name": "name", "is_deleted": False}], "name", "name", operator.eq, 1),
        (
            [
                {"name": "name1", "is_deleted": False},
                {"name": "name2", "is_deleted": False},
            ],
            "name",
            "name1",
            operator.eq,
            1,
        ),
        (
            [
                {"name": "name1", "is_deleted": False},
                {"name": "name2", "is_deleted": False},
            ],
            "is_deleted",
            False,
            operator.is_,
            2,
        ),
    ),
)
def test_count_by_filters(
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

    assert repo.count_by_filters(filters=filters) == 0

    for row in preload:
        insert("table", runner, row)

    assert repo.count_by_filters(filters=filters) == expected_result
