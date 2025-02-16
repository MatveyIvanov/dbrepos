from __future__ import annotations

from typing import Callable, Dict, Type, TypeVar

from core.abstract import IFilter, IFilterSeq, mode, operator
from django.db.models import Field, Q

TTable = TypeVar("TTable")
TFieldValue = TypeVar("TFieldValue", int, str, bytes, float)


_OPERATOR_TO_LOOKUP: Dict[operator, str] = {
    operator.eq: "",
    operator.lt: "__lt",
    operator.le: "__lte",
    operator.gt: "__gt",
    operator.ge: "__gte",
    operator.in_: "__in",
    operator.is_: "",
}


_MODE_TO_ORM: Dict[mode, Callable[[Q], Q]] = {
    mode.and_: Q.__and__,
    mode.or_: Q.__or__,
}


class DjangoFilter(IFilter[TTable]):
    def __init__(
        self,
        table_class: Type[TTable],
        column_name: str,
        value: TFieldValue | None = None,
        operator_: operator = operator.eq,
    ) -> None:
        self.column: Field = getattr(table_class, column_name, None)
        self.column_name = column_name
        self.value = value or None
        self.operator_ = operator_

        assert (
            self.column is not None
        ), f"Model {table_class.__name__} has no column named {column_name}."

    def __call__(
        self,
        value: TFieldValue,
        operator_: operator = operator.eq,
    ) -> IFilter:
        self.value = value
        self.operator_ = operator_
        return self


class DjangoFilterSeq(IFilterSeq):
    def __init__(self, /, mode_: mode, *filters: IFilter | IFilterSeq):
        self.mode_ = mode_
        self.filters = filters

    def compile(self) -> Q:
        result = []
        for filter in self.filters:
            if isinstance(filter, IFilter):
                result.append(
                    Q(
                        **{
                            f"{filter.column_name}{_OPERATOR_TO_LOOKUP[filter.operator_]}": filter.value  # noqa:E501
                        }
                    )
                )
            else:
                result.append(filter.compile())

        return _MODE_TO_ORM[self.mode_](*result)
