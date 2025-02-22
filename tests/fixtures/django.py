import pytest

from repo.django.repo import DjangoRepo
from tests.django.tables.models import DjangoTable


@pytest.fixture
def django_repo_factory():
    def factory(
        table_class=DjangoTable,
        pk_field_name="id",
        is_soft_deletable=False,
        default_ordering=("id",),
    ):
        return DjangoRepo(
            table_class=table_class,
            pk_field_name=pk_field_name,
            is_soft_deletable=is_soft_deletable,
            default_ordering=default_ordering,
        )

    return factory


@pytest.fixture
def django_repo(django_repo_factory):
    return django_repo_factory()


@pytest.fixture
def django_repo_soft_deletable(django_repo_factory):
    return django_repo_factory(is_soft_deletable=True)
