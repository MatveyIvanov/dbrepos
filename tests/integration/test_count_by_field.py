import pytest

from tests.entities import TableEntity
from tests.parametrize import multi_repo_parametrize


@pytest.mark.django_db
@pytest.mark.integration
@multi_repo_parametrize
@pytest.mark.parametrize(
    "preload,name,value,expected_result",
    (
        ([], "name", "name", 0),
        ([{"name": "name", "is_deleted": False}], "name", "unknown", 0),
        ([{"name": "name", "is_deleted": False}], "name", "name", 1),
        (
            [
                {"name": "name1", "is_deleted": False},
                {"name": "name2", "is_deleted": False},
            ],
            "name",
            "name1",
            1,
        ),
        (
            [
                {"name": "name1", "is_deleted": False},
                {"name": "name2", "is_deleted": False},
            ],
            "is_deleted",
            False,
            2,
        ),
    ),
)
def test_count_by_field(
    preload,
    name,
    value,
    expected_result,
    repo,
    runner,
    insert,
    request,
):
    repo = request.getfixturevalue(repo)

    assert repo.count_by_field(name=name, value=value) == 0

    for row in preload:
        insert("table", runner, row)

    assert repo.count_by_field(name=name, value=value) == expected_result
