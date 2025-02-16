from contextlib import AbstractContextManager
from dataclasses import asdict
from typing import TYPE_CHECKING, Iterable, Mapping, Sequence, Tuple, Type, TypeVar
from _typeshed import DataclassInstance

from sqlalchemy import (
    ColumnElement,
    Delete,
    Select,
    Update,
    delete,
    select,
    update,
)
from sqlalchemy.orm import Session

from repo.core.abstract import IFilterSeq, IRepo, mode, operator
from repo.core.types import Extra
from repo.decorators import (
    strict as _strict,
    handle_error as _handle_error,
    session as _session,
)
from repo.sqlalchemy.filters import AlchemyFilter, AlchemyFilterSeq
from repo.shortcuts import get_object_or_404 as _get_object_or_404


TModel = TypeVar("TModel")
TTable = TypeVar("TTable")
if TYPE_CHECKING:
    TEntity = TypeVar("TEntity", bound=DataclassInstance)
else:
    TEntity = TypeVar("TEntity")
TPrimaryKey = TypeVar("TPrimaryKey", int, str)
TFieldValue = TypeVar("TFieldValue", int, str, bytes, float)
TSession = TypeVar("TSession", Session)
TQuery = TypeVar("TQuery", Select, Update, Delete)


strict = _strict
handle_error = _handle_error
session = _session
get_object_or_404 = _get_object_or_404


class Repo(IRepo[TModel]):
    def __init__(
        self,
        *,
        table_class: Type[TTable],
        pk_field_name: str = "id",
        is_soft_deletable: bool = False,
        default_ordering: Tuple[str, ...] = ("id",),
        session_factory: AbstractContextManager | None = None,
    ) -> None:
        self.table_class = table_class
        self.pk_field_name = pk_field_name
        self.is_soft_deletable = is_soft_deletable
        self.default_ordering = default_ordering
        self.session_factory = session_factory

        assert hasattr(self.table_class, self.pk_field_name), "Wrong pk_field"

    @handle_error
    @session
    def create(
        self,
        entity: TEntity,
        *,
        session: TSession | None = None,
    ) -> TTable:
        instance = self.table_class(**asdict(entity))
        session.add(instance)
        session.flush([instance])
        session.refresh(instance)
        return instance

    @handle_error
    @strict
    @session
    def get_by_field(
        self,
        *,
        name: str,
        value: TFieldValue,
        strict: bool = True,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> TTable:
        qs = self._resolve_extra(
            qs=self._select(),
            extra=extra,
        ).filter(getattr(self.table_class, name) == value)
        first = session.execute(qs).first()
        return get_object_or_404(first[0] if first else None)

    @handle_error
    @strict
    @session
    def get_by_filters(
        self,
        *,
        filters: IFilterSeq[ColumnElement[bool]],
        strict: bool = True,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> TTable:
        qs = self._resolve_extra(
            qs=self._select(),
            extra=extra,
        ).filter(filters.compile())
        first = session.execute(qs).first()
        return session.execute(first[0] if first else None)

    @handle_error
    @session
    def get_by_pk(
        self,
        pk: TPrimaryKey,
        *,
        strict: bool = True,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> TTable:
        return self.get_by_field(
            name=self.pk_field_name,
            value=pk,
            strict=strict,
            extra=extra,
            session=session,
        )

    @handle_error
    @session
    def all(
        self,
        *,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> Iterable[TTable]:
        return session.execute(self._resolve_extra(qs=self._select(), extra=extra))

    @handle_error
    @session
    def all_by_field(
        self,
        *,
        name: str,
        value: TFieldValue,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> Iterable[TTable]:
        qs = self._resolve_extra(
            qs=self._select(),
            extra=extra,
        ).filter(getattr(self.table_class, name) == value)
        result = session.execute(qs)
        first = result.first()
        return get_object_or_404(first[0] if first else None)

    @handle_error
    @session
    def all_by_filters(
        self,
        *,
        filters: IFilterSeq,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> Iterable[TTable]:
        qs = self._resolve_extra(
            qs=self._select(),
            extra=extra,
        ).filter(filters.compile())
        return session.execute(qs)

    @handle_error
    @session
    def all_by_pks(
        self,
        pks: Sequence[TPrimaryKey],
        *,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> Iterable[TTable]:
        return self.all_by_filters(
            filters=AlchemyFilterSeq(
                mode.and_,
                AlchemyFilter(
                    table_class=self.table_class,
                    column_name=self.pk_field_name,
                    value=pks,
                    operator_=operator.in_,
                ),
            ),
            extra=extra,
            session=session,
        )

    @handle_error
    @session
    def update(
        self,
        pk: TPrimaryKey,
        *,
        values: Mapping[str, TFieldValue],
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> None:
        session.execute(
            self._resolve_extra(qs=self._update(), extra=extra)
            .filter(getattr(self.table_class, self.pk_field_name) == pk)
            .values(**values)
        )

    @handle_error
    @session
    def multi_update(
        self,
        pks: Sequence[TPrimaryKey],
        *,
        values: Mapping[str, TFieldValue],
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> None:
        session.execute(
            self._resolve_extra(qs=self._update(), extra=extra)
            .filter(getattr(self.table_class, self.pk_field_name).in_(pks))
            .values(**values)
        )

    @handle_error
    @session
    def delete(
        self,
        pk: TPrimaryKey,
        *,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> None:
        session.execute(
            self._resolve_extra(qs=self._delete(), extra=extra).filter(
                getattr(
                    self.table_class,
                    self.pk_field_name,
                )
                == pk
            )
        )

    @handle_error
    @session
    def delete_by_field(
        self,
        *,
        name: str,
        value: TFieldValue,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> None:
        session.execute(
            self._resolve_extra(qs=self._delete(), extra=extra).filter(
                getattr(self.table_class, name) == value
            )
        )

    @handle_error
    @session
    def exists_by_field(
        self,
        *,
        name: str,
        value: TFieldValue,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> bool:
        qs = (
            self._resolve_extra(qs=self._select(), extra=extra)
            .filter(getattr(self.table_class, name) == value)
            .limit(1)
        )
        result = session.execute(qs)
        return result.first() is not None

    @handle_error
    @session
    def exists_by_filters(
        self,
        *,
        filters: IFilterSeq,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> bool:
        qs = (
            self._resolve_extra(qs=self._select(), extra=extra)
            .filter(filters.compile())
            .limit(1)
        )
        result = session.execute(qs)
        return result.first() is not None

    @handle_error
    @session
    def count_by_field(
        self,
        *,
        name: str,
        value: TFieldValue,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> int:
        raise NotImplementedError  # TODO

    @handle_error
    @session
    def count_by_filters(
        self,
        *,
        filters: IFilterSeq,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> int:
        raise NotImplementedError  # TODO

    """ Low-level API """

    def _select(self) -> Select[TModel]:
        return select(self.table_class)

    def _update(self) -> Update[TModel]:
        return update(self.table_class)

    def _delete(self) -> Delete[TModel]:
        return delete(self.table_class)

    """ Utils """

    def _resolve_extra(
        self,
        *,
        qs: TQuery,
        extra: Extra | None,
    ) -> TQuery:
        if not extra:
            return qs
        if isinstance(qs, Select) and extra.for_update:
            qs = qs.with_for_update()
        if self.is_soft_deletable and not extra.include_soft_deleted:
            qs = qs.filter(
                getattr(self.table_class, "is_deleted") == False  # noqa:E712
            )
        if isinstance(qs, Select) and extra.ordering:
            qs = qs.order_by(*extra.ordering)
        return qs
