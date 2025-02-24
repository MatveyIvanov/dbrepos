from dataclasses import fields

import pytest
from django.core.exceptions import FieldError
from sqlalchemy import False_

from repo.core.exceptions import BaseRepoException
from tests.django.tables.models import DjangoTable
from tests.entities import TableEntity


@pytest.mark.django_db
@pytest.mark.integration
@pytest.mark.parametrize(
    "repo,runner",
    (
        ("django_repo", "django"),
        ("django_repo_soft_deletable", "django"),
        ("alchemy_repo", "alchemy"),
        ("alchemy_repo_soft_deletable", "alchemy"),
    ),
)
@pytest.mark.parametrize(
    "preload,name,value,strict,expected_preload_index,expected_error",
    (
        (
            ({"name": "name", "is_deleted": False},),
            "nname",
            "nname",
            False,
            None,
            (KeyError, FieldError),
        ),
        (
            ({"name": "name", "is_deleted": False},),
            "nname",
            "nname",
            True,
            None,
            (KeyError, FieldError),
        ),
        (({"name": "name", "is_deleted": False},), "name", "nname", False, None, None),
        (
            ({"name": "name", "is_deleted": False},),
            "name",
            "nname",
            True,
            None,
            BaseRepoException,
        ),
        (
            ({"name": "name", "is_deleted": False},),
            "name",
            "name",
            False,
            0,
            None,
        ),
        (
            ({"name": "name", "is_deleted": True},),
            "name",
            "name",
            True,
            0,
            None,
        ),
    ),
)
def test_get_by_field_strictness(
    preload,
    name,
    value,
    strict,
    expected_preload_index,
    expected_error,
    repo,
    runner,
    insert,
    request,
):
    repo = request.getfixturevalue(repo)

    ids = []
    for row in preload:
        ids.append(insert("table", runner, row).id)

    if expected_error:
        with pytest.raises(expected_error):
            repo.get_by_field(
                name=name,
                value=value,
                strict=strict,
                convert_to=TableEntity,
            )
    else:
        result = repo.get_by_field(
            name=name,
            value=value,
            strict=strict,
            convert_to=TableEntity,
        )

        if expected_preload_index is not None:
            assert result is not None
            assert isinstance(result, (TableEntity, DjangoTable))
            assert result.id == ids[expected_preload_index]
        else:
            assert result is None
