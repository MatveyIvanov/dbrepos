from unittest import mock

import pytest
from django.db.models import Q

from repo.core.abstract import mode, operator
from repo.django.filters import DjangoFilterSeq, DjangoFilter
from repo.sqlalchemy.filters import AlchemyFilterSeq, AlchemyFilter
from tests.django.tables.models import DjangoTable
from tests.sqlalchemy import AlchemyTable


@pytest.mark.unit
@pytest.mark.parametrize(
    "filterseq_class,mode_,filters,expect_error",
    (
        (DjangoFilterSeq, mode.or_, [], True),
        (DjangoFilterSeq, mode.or_, [DjangoFilter(DjangoTable, "id")], False),
        (AlchemyFilterSeq, mode.or_, [], True),
        (AlchemyFilterSeq, mode.or_, [AlchemyFilter(AlchemyTable, "id")], False),
    ),
)
def test_filterseq_init(filterseq_class, mode_, filters, expect_error):
    if expect_error:
        with pytest.raises(AssertionError):
            filterseq_class(mode_, *filters)
    else:
        filterseq_class(mode_, *filters)


@pytest.mark.unit
@pytest.mark.parametrize(
    "filterseq_class,mode,filters_results,expected_result",
    (
        (DjangoFilterSeq, mode.and_, [Q(id=1)], Q(id=1)),
        (DjangoFilterSeq, mode.or_, [Q(id=1)], Q(id=1)),
        (
            DjangoFilterSeq,
            mode.and_,
            [Q(id=1), Q(name="name")],
            Q(id=1) & Q(name="name"),
        ),
        (
            DjangoFilterSeq,
            mode.or_,
            [Q(id=1), Q(name="name")],
            Q(id=1) | Q(name="name"),
        ),
        (
            DjangoFilterSeq,
            mode.and_,
            [Q(id=1) & Q(is_deleted=False), Q(name="name")],
            Q(id=1) & Q(is_deleted=False) & Q(name="name"),
        ),
        (
            DjangoFilterSeq,
            mode.and_,
            [Q(id=1) | Q(is_deleted=False), Q(name="name")],
            Q(Q(id=1) | Q(is_deleted=False)) & Q(name="name"),
        ),
        (
            DjangoFilterSeq,
            mode.or_,
            [Q(id=1) & Q(is_deleted=False), Q(name="name")],
            Q(id=1) & Q(is_deleted=False) | Q(name="name"),
        ),
        (
            DjangoFilterSeq,
            mode.or_,
            [Q(id=1) | Q(is_deleted=False), Q(name="name")],
            Q(id=1) | Q(is_deleted=False) | Q(name="name"),
        ),
        (
            DjangoFilterSeq,
            mode.and_,
            [Q(name="name"), Q(id=1) & Q(is_deleted=False)],
            Q(name="name") & Q(id=1) & Q(is_deleted=False),
        ),
        (
            DjangoFilterSeq,
            mode.and_,
            [Q(name="name"), Q(id=1) | Q(is_deleted=False)],
            Q(name="name") & Q(Q(id=1) | Q(is_deleted=False)),
        ),
        (
            DjangoFilterSeq,
            mode.or_,
            [Q(name="name"), Q(id=1) & Q(is_deleted=False)],
            Q(name="name") | Q(id=1) & Q(is_deleted=False),
        ),
        (
            DjangoFilterSeq,
            mode.or_,
            [Q(name="name"), Q(id=1) | Q(is_deleted=False)],
            Q(name="name") | Q(id=1) | Q(is_deleted=False),
        ),
        (
            DjangoFilterSeq,
            mode.and_,
            [Q(name="name1") & Q(name="name2"), Q(id=1) & Q(is_deleted=False)],
            Q(name="name1") & Q(name="name2") & Q(id=1) & Q(is_deleted=False),
        ),
        (
            DjangoFilterSeq,
            mode.and_,
            [Q(name="name1") | Q(name="name2"), Q(id=1) & Q(is_deleted=False)],
            Q(Q(name="name1") | Q(name="name2")) & Q(id=1) & Q(is_deleted=False),
        ),
        (
            DjangoFilterSeq,
            mode.and_,
            [Q(name="name1") & Q(name="name2"), Q(id=1) | Q(is_deleted=False)],
            Q(name="name1") & Q(name="name2") & Q(Q(id=1) | Q(is_deleted=False)),
        ),
        (
            DjangoFilterSeq,
            mode.and_,
            [Q(name="name1") | Q(name="name2"), Q(id=1) | Q(is_deleted=False)],
            Q(Q(name="name1") | Q(name="name2")) & Q(Q(id=1) | Q(is_deleted=False)),
        ),
        (
            DjangoFilterSeq,
            mode.or_,
            [Q(name="name1") & Q(name="name2"), Q(id=1) & Q(is_deleted=False)],
            Q(name="name1") & Q(name="name2") | Q(id=1) & Q(is_deleted=False),
        ),
        (
            DjangoFilterSeq,
            mode.or_,
            [Q(name="name1") | Q(name="name2"), Q(id=1) & Q(is_deleted=False)],
            Q(name="name1") | Q(name="name2") | Q(id=1) & Q(is_deleted=False),
        ),
        (
            DjangoFilterSeq,
            mode.or_,
            [Q(name="name1") & Q(name="name2"), Q(id=1) | Q(is_deleted=False)],
            Q(name="name1") & Q(name="name2") | Q(id=1) | Q(is_deleted=False),
        ),
        (
            DjangoFilterSeq,
            mode.or_,
            [Q(name="name1") | Q(name="name2"), Q(id=1) | Q(is_deleted=False)],
            Q(name="name1") | Q(name="name2") | Q(id=1) | Q(is_deleted=False),
        ),
    ),
)
def test_filterseq_compile(filterseq_class, mode, filters_results, expected_result):
    filters = []
    for result in filters_results:
        filter = mock.Mock()
        filter.compile.return_value = result
        filters.append(filter)

    assert str(filterseq_class(mode, *filters).compile()) == str(expected_result)
    for filter in filters:
        filter.compile.assert_called_once_with()
