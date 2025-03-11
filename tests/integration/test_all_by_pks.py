import pytest

from tests.entities import TableEntity
from tests.parametrize import multi_repo_parametrize


@pytest.mark.django_db
@pytest.mark.integration
@multi_repo_parametrize
@pytest.mark.parametrize(
    "preload,pks,expected_result",
    (
        ([], [], []),
        ([], [1], []),
        (
            [{"name": "name", "is_deleted": False}],
            [],
            [],
        ),
        (
            [{"name": "name", "is_deleted": False}],
            [2],
            [],
        ),
        (
            [{"name": "name", "is_deleted": False}],
            [1],
            [TableEntity(id=1, name="name", is_deleted=False)],
        ),
        (
            [
                {"name": "name", "is_deleted": False},
                {"name": "name", "is_deleted": False},
            ],
            [],
            [],
        ),
        (
            [
                {"name": "name", "is_deleted": False},
                {"name": "name", "is_deleted": False},
            ],
            [3, 4],
            [],
        ),
        (
            [
                {"name": "name", "is_deleted": False},
                {"name": "name", "is_deleted": False},
            ],
            [2],
            [TableEntity(id=2, name="name", is_deleted=False)],
        ),
        (
            [
                {"name": "name", "is_deleted": False},
                {"name": "name", "is_deleted": False},
            ],
            [2, 1],
            [
                TableEntity(id=1, name="name", is_deleted=False),
                TableEntity(id=2, name="name", is_deleted=False),
            ],
        ),
    ),
)
def test_all_by_pks(preload, pks, expected_result, repo, runner, insert, request):
    repo = request.getfixturevalue(repo)

    assert repo.all_by_pks(pks=pks, convert_to=TableEntity) == []

    for row in preload:
        insert("table", runner, row)

    assert repo.all_by_pks(pks=pks, convert_to=TableEntity) == expected_result
