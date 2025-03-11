import pytest

from tests.entities import TableEntity
from tests.parametrize import multi_repo_parametrize


@pytest.mark.django_db
@pytest.mark.integration
@multi_repo_parametrize
@pytest.mark.parametrize(
    "preload,pk,expected_result",
    (
        ([], 1, None),
        (
            [{"name": "name", "is_deleted": False}],
            2,
            None,
        ),
        (
            [{"name": "name", "is_deleted": False}],
            1,
            TableEntity(id=1, name="name", is_deleted=False),
        ),
        (
            [
                {"name": "name", "is_deleted": False},
                {"name": "name", "is_deleted": False},
            ],
            3,
            None,
        ),
        (
            [
                {"name": "name", "is_deleted": False},
                {"name": "name", "is_deleted": False},
            ],
            2,
            TableEntity(id=2, name="name", is_deleted=False),
        ),
        (
            [
                {"name": "name", "is_deleted": False},
                {"name": "name", "is_deleted": False},
            ],
            1,
            TableEntity(id=1, name="name", is_deleted=False),
        ),
    ),
)
def test_get_by_pks(preload, pk, expected_result, repo, runner, insert, request):
    repo = request.getfixturevalue(repo)

    assert repo.get_by_pk(pk=pk, strict=False, convert_to=TableEntity) is None

    for row in preload:
        insert("table", runner, row)

    assert (
        repo.get_by_pk(pk=pk, strict=False, convert_to=TableEntity) == expected_result
    )
