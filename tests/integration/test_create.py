from dataclasses import fields

import pytest

from dbrepos.core.abstract import IRepo
from tests.entities import InsertTableEntity, TableEntity
from tests.parametrize import multi_repo_parametrize


@pytest.mark.django_db
@pytest.mark.integration
@multi_repo_parametrize
@pytest.mark.parametrize(
    "entity",
    (
        InsertTableEntity(name="name", is_deleted=True),
        InsertTableEntity(name="name", is_deleted=False),
    ),
)
def test_create(entity, repo, runner, count, select_one, request):
    repo: IRepo = request.getfixturevalue(repo)

    assert count("table", runner) == 0

    instance = repo.create(entity, convert_to=TableEntity)

    assert isinstance(instance, TableEntity) or isinstance(instance, repo.table_class)
    assert getattr(instance, repo.pk_field_name) is not None
    for field in fields(entity):
        assert getattr(instance, field.name) == getattr(entity, field.name)

    assert count("table", runner) == 1
    for field, value in zip(
        fields(TableEntity),
        select_one("table", instance.id, runner),
    ):
        assert getattr(instance, field.name) == value
