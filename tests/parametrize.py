from typing import Tuple, Iterable

import pytest
import sqlalchemy as sa
from django.core.exceptions import FieldError
from django.db.models import Manager, QuerySet

from repo.core.exceptions import BaseRepoException
from tests.django.tables.models import DjangoTable
from tests.entities import TableEntity, InsertTableEntity
from tests.sqlalchemy import AlchemySyncDatabase


multi_repo_parametrize = pytest.mark.parametrize(
    "repo,runner",
    (
        ("django_repo", "django"),
        ("django_repo_soft_deletable", "django"),
        ("alchemy_repo", "alchemy"),
        ("alchemy_repo_soft_deletable", "alchemy"),
    ),
)


methods_parametrize = pytest.mark.parametrize(
    "method,specific_kwargs,returns_many",
    (
        ("create", {"entity": InsertTableEntity(name="name", is_deleted=False)}, False),
        ("get_by_field", {"name": "name", "value": "name", "strict": False}, False),
        ("get_by_filters", {"filters": True, "strict": False}, False),
        ("get_by_pk", {"pk": 1, "strict": False}, False),
        ("all", {}, True),
        ("all_by_field", {"name": "name", "value": "name"}, True),
        ("all_by_filters", {"filters": True}, True),
        ("all_by_pks", {"pks": [1]}, True),
        ("update", {"pk": 1, "values": {"name": "name"}}, False),
        ("multi_update", {"pks": [1], "values": {"name": "name"}}, False),
        ("delete", {"pk": 1}, False),
        ("delete_by_field", {"name": "name", "value": "name"}, False),
        ("exists_by_field", {"name": "name", "value": "name"}, False),
        ("exists_by_filters", {"filters": True}, False),
        ("count_by_field", {"name": "name", "value": "name"}, False),
        ("count_by_filters", {"filters": True}, False),
    ),
)


strict_parametrize = (
    lambda field, value, bad_field_exc: pytest.mark.parametrize(  # noqa:E731
        "preload,name,value,strict,expected_preload_index,expected_error",
        (
            (
                ({"name": "name", "is_deleted": False},),
                f"{field}_unknown",
                value,
                False,
                None,
                bad_field_exc,
            ),
            (
                ({"name": "name", "is_deleted": False},),
                f"{field}_unknown",
                value,
                True,
                None,
                bad_field_exc,
            ),
            (
                ({"name": "name", "is_deleted": False},),
                field,
                f"{value}_unknown",
                False,
                None,
                None,
            ),
            (
                ({"name": "name", "is_deleted": False},),
                field,
                f"{value}_unknown",
                True,
                None,
                BaseRepoException,
            ),
            (
                ({"name": "name", "is_deleted": False},),
                field,
                value,
                False,
                0,
                None,
            ),
            (
                ({"name": "name", "is_deleted": True},),
                field,
                value,
                True,
                0,
                None,
            ),
        ),
    )
)


strictness_by_pk_parametrize = lambda value: pytest.mark.parametrize(  # noqa:E731
    "preload,value,strict,expected_preload_index,expected_error",
    (
        (
            ({"name": "name", "is_deleted": False},),
            value + 1,
            False,
            None,
            None,
        ),
        (
            ({"name": "name", "is_deleted": False},),
            value + 1,
            True,
            None,
            BaseRepoException,
        ),
        (
            ({"name": "name", "is_deleted": False},),
            value,
            False,
            0,
            None,
        ),
        (
            ({"name": "name", "is_deleted": True},),
            value,
            True,
            0,
            None,
        ),
    ),
)


session_parametrize = pytest.mark.parametrize(
    "session_factory,expect_usage,expect_for_runner",
    ((AlchemySyncDatabase.session, True, "alchemy"), (None, False, None)),
)


convert_to_parametrize = pytest.mark.parametrize(
    "convert_to,runner_to_expected_type",
    (
        (
            TableEntity,
            {
                "alchemy": TableEntity,
                "django": (DjangoTable, QuerySet),
            },
        ),
        (
            None,
            {
                "alchemy": (sa.Row, Tuple),
                "django": (DjangoTable, QuerySet),
            },
        ),
    ),
)
