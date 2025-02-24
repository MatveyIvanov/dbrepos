import sqlite3
from typing import Any, Literal

import pytest
import sqlalchemy as sa

from tests.django.tables.models import DjangoTable
from tests.fixtures.django import *  # noqa:F401,F403
from tests.fixtures.sqlalchemy import *  # noqa:F401,F403
from tests.sqlalchemy import AlchemyTable

DB_NAME = "test.db"
# NOTE: I fucking hate django (or pytest-django?)
# for forcing me to do this shit...
# Validating via independent sqlite queries would be amazing,
# but ofc we are doing everything in transaction
# for django (not customizable btw), so sqlite does not see
# db changes until some transaction-committing-related "magic"
# happens in pytest-django fixtures.
# ------------------------------------------------------------
# P.S. Possibly I'm the dumb one here, and there is a way to
# use sqlite-validating queries beside django queries...
Runner = Literal["alchemy", "django"]


@pytest.fixture(scope="session", autouse=True)
def init_db():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("DROP TABLE IF EXISTS 'table';")
    cursor.execute(
        "CREATE TABLE 'table'("
        "id INTEGER PRIMARY KEY ASC,"
        "name TEXT NOT NULL,"
        "is_deleted BOOLEAN NOT NULL"
        ");"
    )

    cursor.close()
    connection.close()


@pytest.fixture(scope="function", autouse=True)
def stateless_db():
    with cursor() as curs:
        curs.execute("DELETE FROM 'table';")

    yield

    with cursor() as curs:
        curs.execute("DELETE FROM 'table';")


class cursor:
    def __enter__(self) -> sqlite3.Cursor:
        self.connection = sqlite3.connect(DB_NAME)
        self.cursor = self.connection.cursor()
        return self.cursor

    def __exit__(self, *args, **kwargs):
        self.connection.commit()
        self.cursor.close()
        self.connection.close()


TABLE_TO_DJANGO = {
    "table": DjangoTable,
}
TABLE_TO_ALCHEMY = {
    "table": AlchemyTable,
}


@pytest.fixture
def sqlitify():
    def _sqlitify(value: Any) -> str:
        if isinstance(value, bool):
            return str(value)

        return f"'{value}'"

    return _sqlitify


@pytest.fixture
def insert(alchemy_session_factory):
    def _insert(table, runner, values):
        def _alchemy():
            with alchemy_session_factory() as session:
                return session.execute(
                    sa.insert(TABLE_TO_ALCHEMY[table])
                    .values(**values)
                    .returning(TABLE_TO_ALCHEMY[table])
                ).one()

        def _django():
            return TABLE_TO_DJANGO[table].objects.create(**values)

        return {
            "alchemy": _alchemy,
            "django": _django,
        }[runner]()

    return _insert


@pytest.fixture
def count(alchemy_session_factory):
    def _count(table: str, runner: Runner):
        def _alchemy():
            with alchemy_session_factory() as session:
                return session.query(TABLE_TO_ALCHEMY[table]).count()

        def _django():
            return TABLE_TO_DJANGO[table].objects.count()

        return {
            "alchemy": _alchemy,
            "django": _django,
        }[runner]()

    return _count


@pytest.fixture
def select(alchemy_session_factory):
    def _select(table: str, runner: Runner):
        def _alchemy():
            with alchemy_session_factory() as session:
                return session.execute(sa.select(TABLE_TO_ALCHEMY[table]))

        def _django():
            return TABLE_TO_DJANGO[table].objects.all().values_list()

        return {
            "alchemy": _alchemy,
            "django": _django,
        }[runner]()

    return _select


@pytest.fixture
def select_one(alchemy_session_factory):
    def _select(table: str, pk: Any, runner: Runner):
        def _alchemy():
            with alchemy_session_factory() as session:
                return session.execute(
                    sa.select(TABLE_TO_ALCHEMY[table]).filter(
                        TABLE_TO_ALCHEMY[table].c.id == pk
                    )
                ).one()

        def _django():
            return TABLE_TO_DJANGO[table].objects.filter(pk=pk).values_list().first()

        return {
            "alchemy": _alchemy,
            "django": _django,
        }[runner]()

    return _select
