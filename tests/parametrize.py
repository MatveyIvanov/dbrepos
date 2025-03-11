from typing import Tuple

import pytest
import sqlalchemy as sa
from django.db.models import QuerySet

from repo.core.exceptions import BaseRepoException
from tests.django.tables.models import DjangoTable
from tests.entities import InsertTableEntity, TableEntity
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
    "method,specific_kwargs,return_type",
    (
        (
            "create",
            {"entity": InsertTableEntity(name="name", is_deleted=False)},
            "instance",
        ),
        (
            "get_by_field",
            {"name": "name", "value": "name", "strict": False},
            "instance",
        ),
        ("get_by_filters", {"filters": True, "strict": False}, "instance"),
        ("get_by_pk", {"pk": 1, "strict": False}, "instance"),
        ("all", {}, "instances"),
        ("all_by_field", {"name": "name", "value": "name"}, "instances"),
        ("all_by_filters", {"filters": True}, "instances"),
        ("all_by_pks", {"pks": [1, 2]}, "instances"),
        ("update", {"pk": 1, "values": {"name": "new"}}, "null"),
        ("multi_update", {"pks": [1, 2], "values": {"name": "new"}}, "null"),
        ("delete", {"pk": 1}, "null"),
        ("delete_by_field", {"name": "name", "value": "name"}, "null"),
        ("exists_by_field", {"name": "name", "value": "name"}, "exists"),
        ("exists_by_filters", {"filters": True}, "exists"),
        ("count_by_field", {"name": "name", "value": "name"}, "count"),
        ("count_by_filters", {"filters": True}, "count"),
    ),
)


strict_parametrize = pytest.mark.parametrize(  # noqa:E731
    "preload,specific_kwargs_override,strict,expected_preload_index,expected_error",
    (
        (
            ({"name": "name", "is_deleted": False},),
            {"name": "name", "value": "unknown", "pk": 2},
            False,
            None,
            None,
        ),
        (
            ({"name": "name", "is_deleted": False},),
            {"name": "name", "value": "unknown", "pk": 2},
            True,
            None,
            BaseRepoException,
        ),
        (
            ({"name": "name", "is_deleted": False},),
            {"name": "name", "value": "name", "pk": 1},
            False,
            0,
            None,
        ),
        (
            ({"name": "name", "is_deleted": False},),
            {"name": "name", "value": "name", "pk": 1},
            True,
            0,
            None,
        ),
    ),
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
                "django": TableEntity,
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


for_update_parametrize = pytest.mark.parametrize(
    "for_update,expect_lock",
    (
        (False, False),
        (True, True),
    ),
)


include_soft_deleted_parametrize = pytest.mark.parametrize(
    "preload,include_soft_deleted,expected_preload_indexes_by_repo_soft_deletable,expected_preload_indexes_overrides_by_method",  # noqa:E501
    (
        (
            (
                {"name": "name", "is_deleted": False},
                {"name": "name", "is_deleted": False},
            ),
            False,
            {False: [0, 1], True: [0, 1]},
            {
                "get_by_field": [0],
                "get_by_filters": [0],
                "get_by_pk": [0],
                "update": [0],
                "delete": [0],
            },
        ),
        (
            (
                {"name": "name", "is_deleted": False},
                {"name": "name", "is_deleted": False},
            ),
            True,
            {False: [0, 1], True: [0, 1]},
            {
                "get_by_field": [0],
                "get_by_filters": [0],
                "get_by_pk": [0],
                "update": [0],
                "delete": [0],
            },
        ),
        (
            (
                {"name": "name", "is_deleted": True},
                {"name": "name", "is_deleted": False},
            ),
            False,
            {False: [0, 1], True: [1]},
            {"get_by_pk": [], "update": [], "delete": []},
        ),
        (
            (
                {"name": "name", "is_deleted": True},
                {"name": "name", "is_deleted": False},
            ),
            True,
            {False: [0, 1], True: [0, 1]},
            {
                "get_by_field": [0],
                "get_by_filters": [0],
                "get_by_pk": [0],
                "update": [0],
                "delete": [0],
            },
        ),
        (
            (
                {"name": "name", "is_deleted": False},
                {"name": "name", "is_deleted": True},
            ),
            False,
            {False: [0, 1], True: [0]},
            {},
        ),
        (
            (
                {"name": "name", "is_deleted": False},
                {"name": "name", "is_deleted": True},
            ),
            True,
            {False: [0, 1], True: [0, 1]},
            {
                "get_by_field": [0],
                "get_by_filters": [0],
                "get_by_pk": [0],
                "update": [0],
                "delete": [0],
            },
        ),
        (
            (
                {"name": "name", "is_deleted": True},
                {"name": "name", "is_deleted": True},
            ),
            False,
            {False: [0, 1], True: []},
            {},
        ),
        (
            (
                {"name": "name", "is_deleted": True},
                {"name": "name", "is_deleted": True},
            ),
            True,
            {False: [0, 1], True: [0, 1]},
            {
                "get_by_field": [0],
                "get_by_filters": [0],
                "get_by_pk": [0],
                "update": [0],
                "delete": [0],
            },
        ),
    ),
)


order_by_parametrize = pytest.mark.parametrize(
    "preload,order_by,expected_preload_indexes,expected_preload_indexes_overrides",
    (
        (
            (
                {"name": "a", "is_deleted": False},
                {"name": "b", "is_deleted": False},
                {"name": "name", "is_deleted": False},
                {"name": "name", "is_deleted": False},
            ),
            None,
            [0, 1, 2, 3],
            {
                "get_by_field": [2],
                "get_by_filters": [0],
                "all_by_field": [2, 3],
                "all_by_pks": [0, 1],
            },
        ),
        (
            (
                {"name": "a", "is_deleted": False},
                {"name": "b", "is_deleted": False},
                {"name": "name", "is_deleted": False},
                {"name": "name", "is_deleted": False},
            ),
            ("id",),
            [0, 1, 2, 3],
            {
                "get_by_field": [2],
                "get_by_filters": [0],
                "all_by_field": [2, 3],
                "all_by_pks": [0, 1],
            },
        ),
        (
            (
                {"name": "a", "is_deleted": False},
                {"name": "b", "is_deleted": False},
                {"name": "name", "is_deleted": False},
                {"name": "name", "is_deleted": False},
            ),
            ("-id",),
            [3, 2, 1, 0],
            {
                "get_by_field": [3],
                "get_by_filters": [3],
                "all_by_field": [3, 2],
                "all_by_pks": [1, 0],
            },
        ),
        (
            (
                {"name": "a", "is_deleted": False},
                {"name": "b", "is_deleted": False},
                {"name": "name", "is_deleted": False},
                {"name": "name", "is_deleted": False},
            ),
            ("name",),
            [0, 1, 2, 3],
            {
                "get_by_field": [2],
                "get_by_filters": [0],
                "all_by_field": [2, 3],
                "all_by_pks": [0, 1],
            },
        ),
        (
            (
                {"name": "a", "is_deleted": False},
                {"name": "b", "is_deleted": False},
                {"name": "name", "is_deleted": False},
                {"name": "name", "is_deleted": False},
            ),
            ("-name",),
            [2, 3, 1, 0],
            {
                "get_by_field": [2],
                "get_by_filters": [2],
                "all_by_field": [2, 3],
                "all_by_pks": [1, 0],
            },
        ),
        (
            (
                {"name": "a", "is_deleted": False},
                {"name": "b", "is_deleted": False},
                {"name": "a", "is_deleted": False},
                {"name": "name", "is_deleted": False},
                {"name": "name", "is_deleted": False},
            ),
            ("-name", "-id"),
            [4, 3, 1, 2, 0],
            {
                "get_by_field": [4],
                "get_by_filters": [4],
                "all_by_field": [4, 3],
                "all_by_pks": [1, 0],
            },
        ),
    ),
)
