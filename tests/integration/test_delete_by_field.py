import pytest

from tests.parametrize import multi_repo_parametrize


@pytest.mark.django_db
@pytest.mark.integration
@multi_repo_parametrize
@pytest.mark.parametrize(
    "preload,name,value,expect_existence_for_indexes",
    (
        ([{"name": "name", "is_deleted": False}], "name", "unknown", {0}),
        ([{"name": "name", "is_deleted": False}], "name", "name", set()),
        (
            [
                {"name": "name1", "is_deleted": False},
                {"name": "name2", "is_deleted": False},
            ],
            "name",
            "name1",
            {1},
        ),
        (
            [
                {"name": "name1", "is_deleted": False},
                {"name": "name2", "is_deleted": False},
            ],
            "is_deleted",
            False,
            set(),
        ),
    ),
)
def test_delete_by_field(
    preload,
    name,
    value,
    expect_existence_for_indexes,
    repo,
    runner,
    insert,
    select_one,
    request,
):
    repo = request.getfixturevalue(repo)

    pks = []
    for row in preload:
        pks.append(insert("table", runner, row).id)
    existing_pks = {pks[index] for index in expect_existence_for_indexes}
    pks = set(pks)
    deleted_pks = pks - existing_pks

    for pk in pks:
        assert select_one("table", pk, runner) is not None
    assert repo.delete_by_field(name=name, value=value) is None
    for pk in existing_pks:
        assert select_one("table", pk, runner) is not None
    for pk in deleted_pks:
        assert select_one("table", pk, runner) is None
