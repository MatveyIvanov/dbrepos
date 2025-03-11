import pytest

from repo.sqlalchemy.repo import AlchemyRepo
from tests.sqlalchemy import AlchemySyncDatabase, AlchemyTable


@pytest.fixture
def alchemy_session_factory():
    return AlchemySyncDatabase.session


@pytest.fixture
def alchemy_repo_factory(alchemy_session_factory):
    def factory(
        table_class=AlchemyTable,
        pk_field_name="id",
        is_soft_deletable=False,
        default_ordering=("id",),
    ):
        return AlchemyRepo(
            table_class=table_class,
            pk_field_name=pk_field_name,
            is_soft_deletable=is_soft_deletable,
            default_ordering=default_ordering,
            session_factory=alchemy_session_factory,
        )

    return factory


@pytest.fixture
def alchemy_repo(alchemy_repo_factory):
    return alchemy_repo_factory()


@pytest.fixture
def alchemy_repo_soft_deletable(alchemy_repo_factory):
    return alchemy_repo_factory(is_soft_deletable=True)
