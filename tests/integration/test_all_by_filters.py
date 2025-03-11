import pytest

from repo.core.types import mode
from tests.entities import TableEntity
from tests.parametrize import multi_repo_parametrize


@pytest.mark.django_db
@pytest.mark.integration
@multi_repo_parametrize
@pytest.mark.parametrize(
    "preload,kwargs,expected_result",
    (
        ([], {"name": "name", "value": "name"}, []),
        (
            [{"name": "name", "is_deleted": False}],
            {"name": "name", "value": "name1"},
            [],
        ),
        (
            [{"name": "name", "is_deleted": False}],
            {"name": "name", "value": "name"},
            [TableEntity(id=1, name="name", is_deleted=False)],
        ),
        (
            [
                {"name": "name1", "is_deleted": False},
                {"name": "name2", "is_deleted": False},
            ],
            {"name": "name", "value": "name1"},
            [TableEntity(id=1, name="name1", is_deleted=False)],
        ),
        (
            [
                {"name": "name", "is_deleted": False},
                {"name": "name", "is_deleted": False},
            ],
            {"name": "name", "value": "name"},
            [
                TableEntity(id=1, name="name", is_deleted=False),
                TableEntity(id=2, name="name", is_deleted=False),
            ],
        ),
    ),
)
def test_all_by_filters(
    preload,
    kwargs,
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
        Filter(runner)(repo.table_class, kwargs["name"], kwargs["value"]),
    )

    assert repo.all_by_filters(filters=filters, convert_to=TableEntity) == []

    for row in preload:
        insert("table", runner, row)

    assert (
        repo.all_by_filters(
            filters=filters,
            convert_to=TableEntity,
        )
        == expected_result
    )
