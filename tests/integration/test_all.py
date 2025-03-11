import pytest

from tests.entities import TableEntity
from tests.parametrize import multi_repo_parametrize


@pytest.mark.django_db
@pytest.mark.integration
@multi_repo_parametrize
@pytest.mark.parametrize(
    "preload,expected_result",
    (
        ([], []),
        (
            [{"name": "name", "is_deleted": False}],
            [TableEntity(id=1, name="name", is_deleted=False)],
        ),
        (
            [
                {"name": "name1", "is_deleted": False},
                {"name": "name2", "is_deleted": False},
            ],
            [
                TableEntity(id=1, name="name1", is_deleted=False),
                TableEntity(id=2, name="name2", is_deleted=False),
            ],
        ),
    ),
)
def test_all(preload, expected_result, repo, runner, insert, request):
    repo = request.getfixturevalue(repo)

    assert repo.all(convert_to=TableEntity) == []

    for row in preload:
        insert("table", runner, row)

    assert repo.all(convert_to=TableEntity) == expected_result
