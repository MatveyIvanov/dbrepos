import pytest

from tests.parametrize import multi_repo_parametrize


@pytest.mark.django_db
@pytest.mark.integration
@multi_repo_parametrize
@pytest.mark.parametrize(
    "preload,name,value,expected_result",
    (
        ([], "name", "name", False),
        ([{"name": "name", "is_deleted": False}], "name", "unknown", False),
        ([{"name": "name", "is_deleted": False}], "name", "name", True),
        (
            [
                {"name": "name1", "is_deleted": False},
                {"name": "name2", "is_deleted": False},
            ],
            "name",
            "name1",
            True,
        ),
        (
            [
                {"name": "name1", "is_deleted": False},
                {"name": "name2", "is_deleted": False},
            ],
            "is_deleted",
            False,
            True,
        ),
    ),
)
def test_exists_by_field(
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

    assert repo.exists_by_field(name=name, value=value) is False

    for row in preload:
        insert("table", runner, row)

    assert repo.exists_by_field(name=name, value=value) is expected_result
