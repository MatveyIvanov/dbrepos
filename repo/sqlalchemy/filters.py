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

from repo.core.abstract import IFilter, IFilterSeq, mode, operator

TTable = TypeVar("TTable")
TFieldValue = TypeVar("TFieldValue")


_OPERATOR_TO_ORM: Dict[
    operator,
    Callable[[Column, TFieldValue], BinaryExpression | ColumnElement],
] = {
    operator.eq: Column.__eq__,
    operator.lt: Column.__lt__,
    operator.le: Column.__le__,
    operator.gt: Column.__gt__,
    operator.ge: Column.__ge__,
    operator.in_: Column.in_,  # type:ignore[dict-item] # this is weird as hell...
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
    mode.and_: and_,  # type:ignore[dict-item] # this is weird as hell...
    mode.or_: or_,  # type:ignore[dict-item] # this is weird as hell...
}


class AlchemyFilter(IFilter[TTable, Column, TFieldValue]):
    def __init__(
        self,
        table_class: Type[TTable],
        column_name: str,
        value: TFieldValue | None = None,
        operator_: operator = operator.eq,
    ) -> None:
        self.column: Column = table_class.c.get(column_name, None)
        self.column_name = column_name
        self.value = value or None
        self.operator_ = operator_

        assert (
            self.column is not None
        ), f"Model {table_class.name} has no column named {column_name}."

    def __call__(
        self, value: TFieldValue, operator_: operator = operator.eq
    ) -> IFilter:
        self.value = value
        self.operator_ = operator_
        return self


class AlchemyFilterSeq(IFilterSeq[BinaryExpression[bool] | ColumnElement[bool]]):
    def __init__(
        self,
        /,
        mode_: mode,
        *filters: (
            IFilter[TTable, Column, TFieldValue]
            | IFilterSeq[BinaryExpression[bool] | ColumnElement[bool]]
        ),
    ) -> None:
        self.mode_ = mode_
        self.filters = filters

        assert len(filters) > 0, "No filters provided."

    def compile(self) -> BinaryExpression[bool] | ColumnElement[bool]:
        result = []
        for filter in self.filters:
            if isinstance(filter, IFilter):
                print(filter.column, filter.value)
                result.append(
                    _OPERATOR_TO_ORM[filter.operator_](
                        filter.column,
                        filter.value,
                    )
                )
            else:
                result.append(filter.compile())

        return _MODE_TO_ORM[self.mode_](*result)
