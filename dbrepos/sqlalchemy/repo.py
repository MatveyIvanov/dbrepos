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
    Row,
    Select,
    Table,
    Update,
    delete,
    insert,
    select,
    update,
)
from sqlalchemy.orm import Query, Session

from dbrepos.core.abstract import IFilterSeq, IRepo, mode, operator
from dbrepos.core.types import Extra
from dbrepos.decorators import TDataclass
from dbrepos.decorators import convert as _convert
from dbrepos.decorators import handle_error as _handle_error
from dbrepos.decorators import session as _session
from dbrepos.decorators import strict as _strict
from dbrepos.shortcuts import get_object_or_404 as _get_object_or_404
from dbrepos.sqlalchemy.filters import AlchemyFilter, AlchemyFilterSeq

TTable = TypeVar("TTable", bound=Table)
if TYPE_CHECKING:
    TEntity = TypeVar("TEntity", bound=DataclassInstance, contravariant=True)
    TResultDataclass = TypeVar("TResultDataclass", bound=DataclassInstance)
else:
    TEntity = TypeVar("TEntity")
    TResultDataclass = TypeVar("TResultDataclass")
TResultORM = TypeVar("TResultORM", bound=Row, covariant=True)
TPrimaryKey = TypeVar("TPrimaryKey", int, str, covariant=True)
TFieldValue = TypeVar("TFieldValue")
TSession = TypeVar("TSession", bound=Session, covariant=True)
TQuery = TypeVar("TQuery", Select, Query, Update, Delete)


strict = _strict
handle_error = _handle_error
session = _session
convert = _convert
get_object_or_404 = _get_object_or_404


class AlchemyRepo(IRepo[TTable, TResultORM]):
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
        convert_to: Type[TDataclass] | None = None,
        session: TSession | None = None,
    ) -> TResultDataclass | TResultORM:
        session = cast(TSession, session)
        return session.execute(  # type:ignore[return-value]
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
        convert_to: Type[TDataclass] | None = None,
        strict: bool = True,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> TResultDataclass | TResultORM | None:
        session = cast(TSession, session)
        qs = self._resolve_extra(
            qs=self._select(),
            extra=extra,
        ).filter(
            self.table_class.c[name]  # type:ignore[index]
            == value
        )
        first = session.execute(qs).first()
        return get_object_or_404(first)  # type:ignore[return-value]

    @handle_error
    @strict
    @session
    @convert(orm="alchemy")
    def get_by_filters(
        self,
        *,
        filters: IFilterSeq[ColumnElement[bool]],
        convert_to: Type[TDataclass] | None = None,
        strict: bool = True,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> TResultDataclass | TResultORM | None:
        session = cast(TSession, session)
        qs = self._resolve_extra(
            qs=self._select(),
            extra=extra,
        ).filter(filters.compile())
        first = session.execute(qs).first()
        return get_object_or_404(first)  # type:ignore[return-value]

    @handle_error
    @session
    def get_by_pk(
        self,
        pk: TPrimaryKey,
        *,
        convert_to: Type[TDataclass] | None = None,
        strict: bool = True,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> TResultDataclass | TResultORM | None:
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
        convert_to: Type[TDataclass] | None = None,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> Iterable[TResultDataclass | TResultORM]:
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
        convert_to: Type[TDataclass] | None = None,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> Iterable[TResultDataclass | TResultORM]:
        session = cast(TSession, session)
        qs = self._resolve_extra(
            qs=self._select(),
            extra=extra,
        ).filter(
            self.table_class.c[name] == value  # type:ignore[index]
        )
        return cast(Iterable, session.execute(qs).all())

    @handle_error
    @session
    @convert(orm="alchemy", many=True)
    def all_by_filters(
        self,
        *,
        filters: IFilterSeq,
        convert_to: Type[TDataclass] | None = None,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> Iterable[TResultDataclass | TResultORM]:
        session = cast(TSession, session)
        qs = self._resolve_extra(
            qs=self._select(),
            extra=extra,
        ).filter(filters.compile())
        return cast(Iterable, session.execute(qs).all())

    @handle_error
    @session
    def all_by_pks(
        self,
        pks: Sequence[TPrimaryKey],
        *,
        convert_to: Type[TDataclass] | None = None,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> Iterable[TResultDataclass | TResultORM]:
        if not pks:
            return []
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
        if not values:
            return
        session = cast(TSession, session)
        session.execute(
            self._resolve_extra(qs=self._update(), extra=extra)
            .filter(self.table_class.c[self.pk_field_name] == pk)  # type:ignore[index]
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
        if not pks or not values:
            return
        session = cast(TSession, session)
        session.execute(
            self._resolve_extra(qs=self._update(), extra=extra)
            .filter(
                self.table_class.c[self.pk_field_name].in_(pks)  # type:ignore[index]
            )
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
                self.table_class.c[self.pk_field_name] == pk  # type:ignore[index]
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
                self.table_class.c[name] == value  # type:ignore[index]
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
            .filter(self.table_class.c[name] == value)  # type:ignore[index]
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
            .filter(self.table_class.c[name] == value)  # type:ignore[index]
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

    def _query(self, session: TSession) -> Query:  # type:ignore[misc]
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
            qs = qs.filter(
                self.table_class.c["is_deleted"]  # type:ignore[index]
                == False  # noqa:E712
            )
        if isinstance(qs, (Select, Query)):
            qs = qs.order_by(
                *self._compile_order_by(extra.ordering or self.default_ordering)
            )
        return qs

    def _compile_order_by(self, ordering: Tuple[str, ...]) -> List:
        compiled = []
        for column in ordering:
            if column.startswith("-"):
                compiled.append(
                    self.table_class.c[column[1:]].desc()  # type:ignore[index]
                )
            else:
                compiled.append(self.table_class.c[column].asc())  # type:ignore[index]
        return compiled
