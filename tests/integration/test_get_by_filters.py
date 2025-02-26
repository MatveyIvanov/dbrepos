from dataclasses import fields

import pytest

from repo.core.abstract import mode, operator
from tests.django.tables.models import DjangoTable
from tests.entities import TableEntity
from tests.parametrize import multi_repo_parametrize, strict_parametrize


@pytest.mark.django_db
@pytest.mark.integration
@multi_repo_parametrize
@strict_parametrize("name", "name", AssertionError)
def test_get_by_filters_strictness(
    preload,
    name,
    value,
    strict,
    expected_preload_index,
    expected_error,
    repo,
    runner,
    insert,
    Filter,
    FilterSeq,
    request,
):
    repo = request.getfixturevalue(repo)

    ids = []
    for row in preload:
        ids.append(insert("table", runner, row).id)

    if expected_error:
        with pytest.raises(expected_error):
            repo.get_by_filters(
                filters=FilterSeq(runner)(
                    mode.and_,
                    Filter(runner)(repo.table_class, name, value, operator.eq),
                ),
                strict=strict,
                convert_to=TableEntity,
            )
    else:
        result = repo.get_by_filters(
            filters=FilterSeq(runner)(
                mode.and_,
                Filter(runner)(repo.table_class, name, value, operator.eq),
            ),
            strict=strict,
            convert_to=TableEntity,
        )

        if expected_preload_index is not None:
            assert result is not None
            assert isinstance(result, (TableEntity, DjangoTable))
            assert result.id == ids[expected_preload_index]
        else:
            assert result is None
