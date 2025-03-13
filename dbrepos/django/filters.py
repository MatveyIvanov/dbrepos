from __future__ import annotations

from typing import Callable, Dict, Self, Type, TypeVar

from django.db.models import Field, Model, Q  # type:ignore[import-untyped]

from dbrepos.core.abstract import IFilter, IFilterSeq, mode, operator

TModel = TypeVar("TModel", bound=Model)
TFieldValue = TypeVar("TFieldValue")


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


class DjangoFilter(IFilter[TModel, Field, TFieldValue, Q]):
    def __init__(
        self,
        table_class: Type[TModel],
        column_name: str,
        value: TFieldValue | None = None,
        operator_: operator = operator.eq,
    ) -> None:
        self.column: Field = getattr(table_class, column_name, None)
        self.column_name = column_name
        self.value = value
        self.operator_ = operator_

        assert (
            self.column is not None
        ), f"Model {table_class.__name__} has no column named {column_name}."

    def __call__(
        self,
        value: TFieldValue,
        operator_: operator = operator.eq,
    ) -> Self:
        self.value = value
        self.operator_ = operator_
        return self

    def compile(self) -> Q:
        return Q(
            **{f"{self.column_name}{_OPERATOR_TO_LOOKUP[self.operator_]}": self.value}
        )


class DjangoFilterSeq(IFilterSeq[Q]):
    def __init__(
        self,
        /,
        mode_: mode,
        *filters: IFilter[TModel, Field, TFieldValue, Q] | IFilterSeq[Q],
    ):
        self.mode_ = mode_
        self.filters = filters

        assert len(self.filters) > 0, "No filters provided."

    def compile(self) -> Q:
        result = []
        for filter in self.filters:
            result.append(filter.compile())

        if len(result) == 1:
            return result[0]
        compiled = result.pop(0)
        while result:
            compiled = _MODE_TO_ORM[self.mode_](
                compiled,
                result.pop(0),  # type:ignore[call-arg]
            )
        return compiled
