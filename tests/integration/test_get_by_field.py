import pytest

from tests.entities import TableEntity
from tests.parametrize import multi_repo_parametrize


@pytest.mark.django_db
@pytest.mark.integration
@multi_repo_parametrize
@pytest.mark.parametrize(
    "preload,kwargs,expected_result",
    (
        ([], {"name": "name", "value": "name"}, None),
        (
            [{"name": "name", "is_deleted": False}],
            {"name": "name", "value": "name1"},
            None,
        ),
        (
            [{"name": "name", "is_deleted": False}],
            {"name": "name", "value": "name"},
            TableEntity(id=1, name="name", is_deleted=False),
        ),
        (
            [
                {"name": "name1", "is_deleted": False},
                {"name": "name2", "is_deleted": False},
            ],
            {"name": "name", "value": "name1"},
            TableEntity(id=1, name="name1", is_deleted=False),
        ),
        (
            [
                {"name": "name", "is_deleted": False},
                {"name": "name", "is_deleted": False},
            ],
            {"name": "name", "value": "name"},
            TableEntity(id=1, name="name", is_deleted=False),
        ),
    ),
)
def test_get_by_field(preload, kwargs, expected_result, repo, runner, insert, request):
    repo = request.getfixturevalue(repo)

    assert repo.get_by_field(**kwargs, strict=False, convert_to=TableEntity) is None

    for row in preload:
        insert("table", runner, row)

    assert (
        repo.get_by_field(**kwargs, strict=False, convert_to=TableEntity)
        == expected_result
    )
