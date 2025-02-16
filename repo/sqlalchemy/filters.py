from __future__ import annotations

from typing import Callable, Dict, Iterable, Literal, Type, TypeVar

from sqlalchemy import (
    BinaryExpression,
    Column,
    ColumnElement,
    ColumnExpressionArgument,
    and_,
    or_,
)

from core.abstract import operator, mode, IFilter, IFilterSeq

TTable = TypeVar("TTable")
TFieldValue = TypeVar("TFieldValue", int, str, bytes, float)


_OPERATOR_TO_ORM: Dict[
    operator,
    Callable[[Column, TFieldValue], BinaryExpression | ColumnElement],
] = {
    operator.eq: Column.__eq__,
    operator.lt: Column.__lt__,
    operator.le: Column.__le__,
    operator.gt: Column.__gt__,
    operator.ge: Column.__ge__,
    operator.in_: Column.in_,
    operator.is_: Column.is_,
}


_MODE_TO_ORM: Dict[
    mode,
    Callable[
        [
            ColumnExpressionArgument[bool] | Literal[False, True],
            Iterable[ColumnExpressionArgument[bool]],
        ],
        ColumnElement[bool],
    ],
] = {
    mode.and_: and_,
    mode.or_: or_,
}


class AlchemyFilter(IFilter[TTable]):
    def __init__(
        self,
        table_class: Type[TTable],
        column_name: str,
        value: TFieldValue | None = None,
        operator_: operator = operator.eq,
    ) -> None:
        self.column: Column = getattr(table_class, column_name, None)
        self.column_name = column_name
        self.value = value or None
        self.operator_ = operator_

        assert (
            self.column is not None
        ), f"Model {table_class.__name__} has no column named {column_name}."

    def __call__(
        self, value: TFieldValue, operator_: operator = operator.eq
    ) -> IFilter:
        self.value = value
        self.operator_ = operator_
        return self


class AlchemyFilterSeq(IFilterSeq):
    def __init__(self, /, mode_: mode, *filters: IFilter | IFilterSeq):
        self.mode_ = mode_
        self.filters = filters

    def compile(self) -> ColumnElement[bool]:
        result = []
        for filter in self.filters:
            if isinstance(filter, IFilter):
                result.append(
                    _OPERATOR_TO_ORM[filter.operator_](
                        filter.column,
                        filter.value,
                    )
                )
            else:
                result.append(filter.compile())

        return _MODE_TO_ORM[self.mode_](*result)
