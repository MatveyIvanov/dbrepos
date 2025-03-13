import pytest

from dbrepos.django.repo import DjangoRepo
from dbrepos.sqlalchemy.repo import AlchemyRepo
from tests.django.tables.models import DjangoTable
from tests.sqlalchemy import AlchemySyncDatabase, AlchemyTable


@pytest.mark.unit
@pytest.mark.parametrize(
    "repo_class,kwargs,expect_error",
    (
        (DjangoRepo, {"table_class": DjangoTable, "pk_field_name": "id"}, False),
        (DjangoRepo, {"table_class": DjangoTable, "pk_field_name": "pk"}, False),
        (DjangoRepo, {"table_class": DjangoTable, "pk_field_name": "od"}, True),
        (
            AlchemyRepo,
            {
                "table_class": AlchemyTable,
                "pk_field_name": "id",
                "session_factory": AlchemySyncDatabase.session,
            },
            False,
        ),
        (
            AlchemyRepo,
            {
                "table_class": AlchemyTable,
                "pk_field_name": "id",
            },
            True,
        ),
        (
            AlchemyRepo,
            {
                "table_class": AlchemyTable,
                "pk_field_name": "pk",
                "session_factory": AlchemySyncDatabase.session,
            },
            True,
        ),
        (
            AlchemyRepo,
            {
                "table_class": AlchemyTable,
                "pk_field_name": "pk",
            },
            True,
        ),
    ),
)
def test_init(repo_class, kwargs, expect_error):
    if expect_error:
        with pytest.raises(AssertionError):
            repo_class(**kwargs)
    else:
        repo_class(**kwargs)
