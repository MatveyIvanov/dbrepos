import pytest
from django.db.models import Q

from repo.core.abstract import operator
from repo.django.filters import DjangoFilter
from repo.sqlalchemy.filters import AlchemyFilter
from tests.django.tables.models import DjangoTable
from tests.sqlalchemy import AlchemyTable


@pytest.mark.unit
@pytest.mark.parametrize(
    "filter_class,table_class,column_name,value,operator,expected_column,expected_value,expected_operator,expect_error",
    (
        (
            DjangoFilter,
            DjangoTable,
            "id",
            1,
            operator.in_,
            DjangoTable.id,
            1,
            operator.in_,
            False,
        ),
        (
            DjangoFilter,
            DjangoTable,
            "id",
            "",
            operator.in_,
            DjangoTable.id,
            None,
            operator.in_,
            False,
        ),
        (
            DjangoFilter,
            DjangoTable,
            "ids",
            1,
            operator.in_,
            DjangoTable.id,
            1,
            operator.in_,
            True,
        ),
        (
            AlchemyFilter,
            AlchemyTable,
            "id",
            1,
            operator.in_,
            AlchemyTable.c.id,
            1,
            operator.in_,
            False,
        ),
        (
            AlchemyFilter,
            AlchemyTable,
            "id",
            "",
            operator.in_,
            AlchemyTable.c.id,
            None,
            operator.in_,
            False,
        ),
        (
            AlchemyFilter,
            AlchemyTable,
            "ids",
            1,
            operator.in_,
            AlchemyTable.c.id,
            1,
            operator.in_,
            True,
        ),
    ),
)
def test_filter_first_step(
    filter_class,
    table_class,
    column_name,
    value,
    operator,
    expected_column,
    expected_value,
    expected_operator,
    expect_error,
):
    if expect_error:
        with pytest.raises(AssertionError):
            filter_class(table_class, column_name, value, operator)
        return

    filter = filter_class(table_class, column_name, value, operator)

    assert filter.column == expected_column
    assert filter.value == expected_value
    assert filter.operator_ == expected_operator


@pytest.mark.unit
@pytest.mark.parametrize(
    "filter,value,operator,expected_value,expected_operator",
    (
        (
            DjangoFilter(DjangoTable, "id", 1, operator.in_),
            2,
            operator.eq,
            2,
            operator.eq,
        ),
        (
            AlchemyFilter(AlchemyTable, "id", 1, operator.in_),
            2,
            operator.eq,
            2,
            operator.eq,
        ),
    ),
)
def test_filter_second_step(filter, value, operator, expected_value, expected_operator):
    filter(value, operator)

    assert filter.value == expected_value
    assert filter.operator_ == expected_operator


@pytest.mark.unit
@pytest.mark.parametrize(
    "filter,expected_compiled",
    (
        (DjangoFilter(DjangoTable, "id", 1, operator.eq), Q(id=1)),
        (DjangoFilter(DjangoTable, "id", 1, operator.lt), Q(id__lt=1)),
        (DjangoFilter(DjangoTable, "id", 1, operator.le), Q(id__lte=1)),
        (DjangoFilter(DjangoTable, "id", 1, operator.gt), Q(id__gt=1)),
        (DjangoFilter(DjangoTable, "id", 1, operator.ge), Q(id__gte=1)),
        (DjangoFilter(DjangoTable, "id", [1], operator.in_), Q(id__in=[1])),
        (DjangoFilter(DjangoTable, "id", 1, operator.is_), Q(id=1)),
        (AlchemyFilter(AlchemyTable, "id", 1, operator.eq), '"table".id = :id_1'),
        (AlchemyFilter(AlchemyTable, "id", 1, operator.lt), '"table".id < :id_1'),
        (AlchemyFilter(AlchemyTable, "id", 1, operator.le), '"table".id <= :id_1'),
        (AlchemyFilter(AlchemyTable, "id", 1, operator.gt), '"table".id > :id_1'),
        (AlchemyFilter(AlchemyTable, "id", 1, operator.ge), '"table".id >= :id_1'),
        (
            AlchemyFilter(AlchemyTable, "id", [1], operator.in_),
            '"table".id IN (__[POSTCOMPILE_id_1])',
        ),
        (AlchemyFilter(AlchemyTable, "id", 1, operator.is_), '"table".id IS :id_1'),
    ),
)
def test_filter_compile(filter, expected_compiled):
    assert str(filter.compile()) == str(expected_compiled)
