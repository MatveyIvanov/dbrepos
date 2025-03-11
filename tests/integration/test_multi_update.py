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
        inserted_pks.append(("table", runner, row).id)

    assert repo.multi_update(pks=pks, values=values) is None
    assert select("table", runner) == expected_result
