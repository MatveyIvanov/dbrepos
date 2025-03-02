from contextlib import AbstractContextManager
from dataclasses import asdict
from typing import (
    TYPE_CHECKING,
    Iterable,
    List,
    Mapping,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    cast,
)

if TYPE_CHECKING:
    from _typeshed import DataclassInstance

from sqlalchemy import (
    ColumnElement,
    Delete,
    Select,
    Update,
    delete,
    insert,
    select,
    update,
)
from sqlalchemy.orm import Query, Session

from repo.core.abstract import IFilterSeq, IRepo, mode, operator
from repo.core.types import Extra
from repo.decorators import convert as _convert
from repo.decorators import handle_error as _handle_error
from repo.decorators import session as _session
from repo.decorators import strict as _strict
from repo.shortcuts import get_object_or_404 as _get_object_or_404
from repo.sqlalchemy.filters import AlchemyFilter, AlchemyFilterSeq

TTable = TypeVar("TTable")
if TYPE_CHECKING:
    TEntity = TypeVar("TEntity", bound=DataclassInstance)
    TResult = TypeVar("TEntity", TTable, DataclassInstance)
else:
    TEntity = TypeVar("TEntity")
    TResult = TypeVar("TEntity", bound=TTable)
TPrimaryKey = TypeVar("TPrimaryKey", int, str)
TFieldValue = TypeVar("TFieldValue")
TSession = TypeVar("TSession", bound=Session)
TQuery = TypeVar("TQuery", Select, Query, Update, Delete)


strict = _strict
handle_error = _handle_error
session = _session
convert = _convert
get_object_or_404 = _get_object_or_404


class AlchemyRepo(IRepo[TTable]):
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

        assert (
            session_factory is not None
        ), "Session factory is required for AlchemyRepo"
        assert hasattr(self.table_class, self.pk_field_name) or hasattr(
            self.table_class.c, self.pk_field_name
        ), "Wrong pk_field_name"

    @handle_error
    @session
    @convert(orm="alchemy")
    def create(
        self,
        entity: TEntity,
        *,
        session: TSession | None = None,
        convert_to: TResult | None = None,
    ) -> TTable:
        session = cast(TSession, session)
        return session.execute(
            insert(self.table_class)
            .values(**asdict(entity))
            .returning(self.table_class)
        ).one()

    @handle_error
    @strict
    @session
    @convert(orm="alchemy")
    def get_by_field(
        self,
        *,
        name: str,
        value: TFieldValue,
        strict: bool = True,
        extra: Extra | None = None,
        session: TSession | None = None,
        convert_to: TResult | None = None,
    ) -> TTable:
        session = cast(TSession, session)
        qs = self._resolve_extra(
            qs=self._select(),
            extra=extra,
        ).filter(
            self.table_class.c[name]  # TODO: alternative table definition support
            == value
        )
        first = session.execute(qs).first()
        return get_object_or_404(first)

    @handle_error
    @strict
    @session
    @convert(orm="alchemy")
    def get_by_filters(
        self,
        *,
        filters: IFilterSeq[ColumnElement[bool]],
        strict: bool = True,
        extra: Extra | None = None,
        session: TSession | None = None,
        convert_to: TResult | None = None,
    ) -> TTable:
        session = cast(TSession, session)
        qs = self._resolve_extra(
            qs=self._select(),
            extra=extra,
        ).filter(filters.compile())
        first = session.execute(qs).first()
        return get_object_or_404(first)

    @handle_error
    @session
    def get_by_pk(
        self,
        pk: TPrimaryKey,
        *,
        strict: bool = True,
        extra: Extra | None = None,
        session: TSession | None = None,
        convert_to: TResult | None = None,
    ) -> TTable:
        session = cast(TSession, session)
        return self.get_by_field(
            name=self.pk_field_name,
            value=pk,
            strict=strict,
            extra=extra,
            session=session,
            convert_to=convert_to,
        )

    @handle_error
    @session
    @convert(orm="alchemy", many=True)
    def all(
        self,
        *,
        extra: Extra | None = None,
        session: TSession | None = None,
        convert_to: TResult | None = None,
    ) -> Iterable[TTable]:
        session = cast(TSession, session)
        return session.execute(  # type:ignore[return-value] # Though Result is iterable
            self._resolve_extra(qs=self._select(), extra=extra)
        ).all()

    @handle_error
    @session
    @convert(orm="alchemy", many=True)
    def all_by_field(
        self,
        *,
        name: str,
        value: TFieldValue,
        extra: Extra | None = None,
        session: TSession | None = None,
        convert_to: TResult | None = None,
    ) -> Iterable[TTable]:
        session = cast(TSession, session)
        qs = self._resolve_extra(
            qs=self._select(),
            extra=extra,
        ).filter(self.table_class.c[name] == value)
        return session.execute(qs).all()

    @handle_error
    @session
    @convert(orm="alchemy", many=True)
    def all_by_filters(
        self,
        *,
        filters: IFilterSeq,
        extra: Extra | None = None,
        session: TSession | None = None,
        convert_to: TResult | None = None,
    ) -> Iterable[TTable]:
        session = cast(TSession, session)
        qs = self._resolve_extra(
            qs=self._select(),
            extra=extra,
        ).filter(filters.compile())
        return session.execute(  # type:ignore[return-value] # Though Result is iterable
            qs
        ).all()

    @handle_error
    @session
    def all_by_pks(
        self,
        pks: Sequence[TPrimaryKey],
        *,
        extra: Extra | None = None,
        session: TSession | None = None,
        convert_to: TResult | None = None,
    ) -> Iterable[TTable]:
        session = cast(TSession, session)
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
            convert_to=convert_to,
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
        session = cast(TSession, session)
        session.execute(
            self._resolve_extra(qs=self._update(), extra=extra)
            .filter(self.table_class.c[self.pk_field_name] == pk)
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
        session = cast(TSession, session)
        session.execute(
            self._resolve_extra(qs=self._update(), extra=extra)
            .filter(self.table_class.c[self.pk_field_name].in_(pks))
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
        session = cast(TSession, session)
        session.execute(
            self._resolve_extra(qs=self._delete(), extra=extra).filter(
                self.table_class.c[self.pk_field_name] == pk
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
        session = cast(TSession, session)
        session.execute(
            self._resolve_extra(qs=self._delete(), extra=extra).filter(
                self.table_class.c[name] == value
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
        session = cast(TSession, session)
        qs = (
            self._resolve_extra(qs=self._select(), extra=extra)
            .filter(self.table_class.c[name] == value)
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
        session = cast(TSession, session)
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
        session = cast(TSession, session)
        return (
            self._resolve_extra(
                qs=self._query(session),
                extra=extra,
            )
            .filter(self.table_class.c[name] == value)
            .count()
        )

    @handle_error
    @session
    def count_by_filters(
        self,
        *,
        filters: IFilterSeq,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> int:
        session = cast(TSession, session)
        return (
            self._resolve_extra(
                qs=self._query(session),
                extra=extra,
            )
            .filter(filters.compile())
            .count()
        )

    """ Low-level API """

    def _select(self) -> Select:
        return select(self.table_class)

    def _update(self) -> Update:
        return update(self.table_class)

    def _delete(self) -> Delete:
        return delete(self.table_class)

    def _query(self, session: TSession) -> Query:
        return session.query(self.table_class)

    """ Utils """

    def _resolve_extra(
        self,
        *,
        qs: TQuery,
        extra: Extra | None,
    ) -> TQuery:
        if not extra:
            extra = Extra()
        if isinstance(qs, (Select, Query)) and extra.for_update:
            qs = qs.with_for_update()
        if self.is_soft_deletable and not extra.include_soft_deleted:
            qs = qs.filter(self.table_class.c["is_deleted"] == False)  # noqa:E712
        if isinstance(qs, (Select, Query)):
            qs = qs.order_by(
                *self._compile_order_by(extra.ordering or self.default_ordering)
            )
        return qs

    def _compile_order_by(self, ordering: Tuple[str, ...]) -> List:
        compiled = []
        for column in ordering:
            if column.startswith("-"):
                compiled.append(self.table_class.c[column[1:]].desc())
            else:
                compiled.append(self.table_class.c[column].asc())
        return compiled
