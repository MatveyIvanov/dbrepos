from dataclasses import fields

import pytest

from tests.parametrize import multi_repo_parametrize, session_parametrize
import pytest

from repo.core.types import mode, operator
from tests.parametrize import multi_repo_parametrize, session_parametrize
import pytest

from tests.entities import TableEntity
from tests.parametrize import multi_repo_parametrize


@pytest.mark.django_db
@pytest.mark.integration
@multi_repo_parametrize
@pytest.mark.parametrize(
    "preload,pk,values,expected_result",
    (
        (
            {"name": "name", "is_deleted": False},
            1,
            {},
            TableEntity(id=1, name="name", is_deleted=False),
        ),
        (
            {"name": "name", "is_deleted": False},
            1,
            {"name": "new name"},
            TableEntity(id=1, name="new name", is_deleted=False),
        ),
        (
            {"name": "name", "is_deleted": False},
            1,
            {"is_deleted": True},
            TableEntity(id=1, name="name", is_deleted=True),
        ),
        (
            {"name": "name", "is_deleted": False},
            1,
            {"name": "new name", "is_deleted": True},
            TableEntity(id=1, name="new name", is_deleted=True),
        ),
    ),
)
def test_update(
    preload,
    pk,
    values,
    expected_result,
    repo,
    runner,
    insert,
    select_one,
    request,
):
    repo = request.getfixturevalue(repo)

    inserted_pk = insert("table", runner, preload).id

    assert repo.update(pk=pk, values=values) is None
    assert select_one("table", inserted_pk, runner, TableEntity) == expected_result
