import pytest

from tests.parametrize import multi_repo_parametrize


@pytest.mark.django_db
@pytest.mark.integration
@multi_repo_parametrize
@pytest.mark.parametrize(
    "preload,pks,values,expected_result",
    (
        (
            [{"name": "name", "is_deleted": False}],
            [1],
            {},
            [(1, "name", False)],
        ),
        (
            [{"name": "name", "is_deleted": False}],
            [1],
            {"name": "new name"},
            [(1, "new name", False)],
        ),
        (
            [{"name": "name", "is_deleted": False}],
            [1],
            {"is_deleted": True},
            [(1, "name", True)],
        ),
        (
            [{"name": "name", "is_deleted": False}],
            [1],
            {"name": "new name", "is_deleted": True},
            [(1, "new name", True)],
        ),
        (
            [
                {"name": "name1", "is_deleted": False},
                {"name": "name2", "is_deleted": False},
            ],
            [2],
            {"name": "new name", "is_deleted": True},
            [(1, "name1", False), (2, "new name", True)],
        ),
        (
            [
                {"name": "name1", "is_deleted": False},
                {"name": "name2", "is_deleted": False},
            ],
            [1, 2],
            {"name": "new name", "is_deleted": True},
            [(1, "new name", True), (2, "new name", True)],
        ),
    ),
)
def test_multi_update(
    preload,
    pks,
    values,
    expected_result,
    repo,
    runner,
    insert,
    select,
    request,
):
    repo = request.getfixturevalue(repo)

    inserted_pks = []
    for row in preload:
        inserted_pks.append(insert("table", runner, row).id)

    assert repo.multi_update(pks=pks, values=values) is None
    assert list(select("table", runner)) == expected_result
