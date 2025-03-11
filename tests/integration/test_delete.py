import pytest

from tests.parametrize import multi_repo_parametrize


@pytest.mark.django_db
@pytest.mark.integration
@multi_repo_parametrize
@pytest.mark.parametrize(
    "preload,pk,expect_existence",
    (
        ({"name": "name", "is_deleted": False}, 2, True),
        ({"name": "name", "is_deleted": False}, 1, False),
    ),
)
def test_delete(
    preload,
    pk,
    expect_existence,
    repo,
    runner,
    insert,
    select_one,
    request,
):
    repo = request.getfixturevalue(repo)

    inserted_pk = insert("table", runner, preload).id

    assert select_one("table", inserted_pk, runner) is not None
    assert repo.delete(pk=pk) is None
    if expect_existence:
        assert select_one("table", inserted_pk, runner) is not None
    else:
        assert select_one("table", inserted_pk, runner) is None
