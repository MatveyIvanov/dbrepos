from __future__ import annotations

from contextlib import AbstractContextManager
from enum import IntEnum
from typing import (
    TYPE_CHECKING,
    Iterable,
    Literal,
    Mapping,
    Protocol,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    overload,
    runtime_checkable,
)
from _typeshed import DataclassInstance

from repo.core.types import Extra

TTable = TypeVar("TTable")
TColumn = TypeVar("TColumn")
if TYPE_CHECKING:
    TEntity = TypeVar("TEntity", bound=DataclassInstance, contravariant=True)
else:
    TEntity = TypeVar("TEntity")
TCompiledFilter = TypeVar("TCompiledFilter", covariant=True)
TPrimaryKey = TypeVar("TPrimaryKey", int, str, covariant=True)
TFieldValue = TypeVar("TFieldValue")
TSession = TypeVar("TSession", covariant=True)


class IRepo(Protocol[TTable]):
    table_class: Type[TTable]
    pk_field_name: str
    is_soft_deletable: bool
    default_ordering: Tuple[str, ...]
    session_factory: AbstractContextManager | None

    def __init__(
        self,
        *,
        table_class: Type[TTable],
        pk_field_name: str = "id",
        is_soft_deletable: bool = False,
        default_ordering: Tuple[str, ...] = ("id",),
        session_factory: AbstractContextManager | None = None,
    ) -> None:
        """
        Construct a repo instance

        Args:
            table_class (Type[TTable]): DB table class
            pk_field_name (str, optional): Name of the primary key field.
                Defaults to "id"
            is_soft_deletable (bool, optional): Is table soft deletable.
                Defaults to False
            default_ordering (Tuple[str, ...], optional): Default ordering.
                Defaults to ("id",)
            session_factory (AbstractContextManager | None, optional):
                Factory for the session.
                Currently supported to SQLAlchemy
        """

    def create(
        self,
        entity: TEntity,
        *,
        session: TSession | None = None,
    ) -> TTable:
        """
        Insert row

        Args:
            entity (TEntity): Entity that should be inserted
            session (TSession | None): Session to use for DB queries.
                Defaults to None.
                Currently supported for SQLAlchemy

        Returns:
            TTable: Inserted row
        """

    @overload
    def get_by_field(
        self,
        *,
        name: str,
        value: TFieldValue,
        strict: Literal[True] = True,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> TTable:
        """
        Get row by field:value

        Args:
            name (str): Name of the field
            value (TFieldValue): Value of the field
            strict (bool): Raise exception for missing row.
                Works only for single-row select.
                Defaults to True.
            extra (Extra | None, optional): Extra params.
                Defaults to None
            session (TSession | None): Session to use for DB queries.
                Defaults to None.
                Currently supported for SQLAlchemy

        Returns:
            Iterable[TTable]: Found row
        """

    @overload
    def get_by_field(
        self,
        *,
        name: str,
        value: TFieldValue,
        strict: Literal[False],
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> TTable | None:
        """
        Get row by field:value

        Args:
            name (str): Name of the field
            value (TFieldValue): Value of the field
            strict (bool): Raise exception for missing row.
                Works only for single-row select.
                Defaults to True.
            extra (Extra | None, optional): Extra params.
                Defaults to None
            session (TSession | None): Session to use for DB queries.
                Defaults to None.
                Currently supported for SQLAlchemy

        Returns:
            Iterable[TTable | None]: Found row or None
        """

    @overload
    def get_by_filters(
        self,
        *,
        filters: IFilterSeq,
        strict: Literal[True] = True,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> TTable:
        """
        Get row by filters

        Args:
            filters (IFilterSeq): Filter sequence
            strict (bool): Raise exception for missing row.
                Works only for single-row select.
                Defaults to True.
            extra (Extra | None, optional): Extra params.
                Defaults to None
            session (TSession | None): Session to use for DB queries.
                Defaults to None.
                Currently supported for SQLAlchemy

        Returns:
            TTable: Found row
        """

    @overload
    def get_by_filters(
        self,
        *,
        filters: IFilterSeq,
        strict: Literal[False],
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> TTable:
        """
        Get row by filters

        Args:
            filters (IFilterSeq): Filter sequence
            strict (bool): Raise exception for missing row.
                Works only for single-row select.
                Defaults to True.
            extra (Extra | None, optional): Extra params.
                Defaults to None
            session (TSession | None): Session to use for DB queries.
                Defaults to None.
                Currently supported for SQLAlchemy

        Returns:
            TTable | None: Found row or None
        """

    @overload
    def get_by_pk(
        self,
        pk: TPrimaryKey,
        *,
        strict: Literal[True] = True,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> TTable:
        """
        Get row by primary key

        Args:
            pk (TPrimaryKey): Primary key value
            strict (bool): Raise exception for missing row.
                Works only for single-row select.
                Defaults to True.
            extra (Extra | None, optional): Extra params.
                Defaults to None
            session (TSession | None): Session to use for DB queries.
                Defaults to None.
                Currently supported for SQLAlchemy

        Returns:
            TTable: Found row
        """

    @overload
    def get_by_pk(
        self,
        pk: TPrimaryKey,
        *,
        strict: Literal[False],
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> TTable | None:
        """
        Get row by primary key

        Args:
            pk (TPrimaryKey): Primary key value
            strict (bool): Raise exception for missing row.
                Works only for single-row select.
                Defaults to True.
            extra (Extra | None, optional): Extra params.
                Defaults to None
            session (TSession | None): Session to use for DB queries.
                Defaults to None.
                Currently supported for SQLAlchemy

        Returns:
            TTable | None: Found row or None
        """

    def all(
        self,
        *,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> Iterable[TTable]:
        """
        Select rows

        Args:
            extra (Extra | None, optional): Extra params.
                Defaults to None
            session (TSession | None): Session to use for DB queries.
                Defaults to None.
                Currently supported for SQLAlchemy

        Returns:
            Iterable[TTable]: Found rows
        """

    def all_by_field(
        self,
        *,
        name: str,
        value: TFieldValue,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> Iterable[TTable]:
        """
        Get rows by field:value

        Args:
            name (str): Name of the field
            value (TFieldValue): Value of the field
            extra (Extra | None, optional): Extra params.
                Defaults to None
            session (TSession | None): Session to use for DB queries.
                Defaults to None.
                Currently supported for SQLAlchemy

        Returns:
            Iterable[TTable]: Found rows
        """

    def all_by_filters(
        self,
        *,
        filters: IFilterSeq,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> Iterable[TTable]:
        """
        Get rows by filters

        Args:
            filters (IFilterSeq): Filter sequence
            extra (Extra | None, optional): Extra params.
                Defaults to None
            session (TSession | None): Session to use for DB queries.
                Defaults to None.
                Currently supported for SQLAlchemy

        Returns:
            Iterable[TTable]: Found rows
        """

    def all_by_pks(
        self,
        pks: Sequence[TPrimaryKey],
        *,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> Iterable[TTable]:
        """
        Get rows by primary keys

        Args:
            pks (Sequence[TPrimaryKey]): Primary key values
            extra (Extra | None, optional): Extra params.
                Defaults to None
            session (TSession | None): Session to use for DB queries.
                Defaults to None.
                Currently supported for SQLAlchemy

        Returns:
            Iterable[TTable]: Found rows
        """

    def update(
        self,
        pk: TPrimaryKey,
        *,
        values: Mapping[str, TFieldValue],
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> None:
        """
        Update row

        Args:
            pk (TPrimaryKey): Primary key of row to update
            values (Mapping[str, TFieldValue]): Mapping with
                format {field_name:new_value}
            extra (Extra | None, optional): Extra params.
                Defaults to None
            session (TSession | None): Session to use for DB queries.
                Defaults to None.
                Currently supported for SQLAlchemy
        """

    def multi_update(
        self,
        pks: Sequence[TPrimaryKey],
        *,
        values: Mapping[str, TFieldValue],
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> None:
        """
        Update rows

        Args:
            pks (Sequence[TPrimaryKey]): Primary keys of rows to update
            values (Mapping[str, TFieldValue]): Mapping with
                format {field_name:new_value}
            extra (Extra | None, optional): Extra params.
                Defaults to None
            session (TSession | None): Session to use for DB queries.
                Defaults to None.
                Currently supported for SQLAlchemy
        """

    def delete(
        self,
        pk: TPrimaryKey,
        *,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> None:
        """
        Delete row by pk

        Args:
            pk (TPrimaryKey): Primary key of row to delete
            extra (Extra | None, optional): Extra params.
                Defaults to None
            session (TSession | None): Session to use for DB queries.
                Defaults to None.
                Currently supported for SQLAlchemy
        """

    def delete_by_field(
        self,
        *,
        name: str,
        value: TFieldValue,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> None:
        """
        Delete row by field:value

        Args:
            name (str): Name of the field
            value (TFieldValue): Value of the field
            extra (Extra | None, optional): Extra params.
                Defaults to None
            session (TSession | None): Session to use for DB queries.
                Defaults to None.
                Currently supported for SQLAlchemy
        """

    def exists_by_field(
        self,
        *,
        name: str,
        value: TFieldValue,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> bool:
        """
        Check if row exists by field:value

        Args:
            name (str): Name of the field
            value (TFieldValue): Value of the field
            extra (Extra | None, optional): Extra params.
                Defaults to None
            session (TSession | None): Session to use for DB queries.
                Defaults to None.
                Currently supported for SQLAlchemy

        Returns:
            bool: Row existence
        """

    def exists_by_filters(
        self,
        *,
        filters: IFilterSeq,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> bool:
        """
        Check if row exists by filters

        Args:
            filters (IFilterSeq): Filter sequence
            extra (Extra | None, optional): Extra params.
                Defaults to None
            session (TSession | None): Session to use for DB queries.
                Defaults to None.
                Currently supported for SQLAlchemy

        Returns:
            bool: Row existence
        """

    def count_by_field(
        self,
        *,
        name: str,
        value: TFieldValue,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> int:
        """
        Count rows by field:value

        Args:
            name (str): Name of the field
            value (TFieldValue): Value of the field
            extra (Extra | None, optional): Extra params.
                Defaults to None
            session (TSession | None): Session to use for DB queries.
                Defaults to None.
                Currently supported for SQLAlchemy

        Returns:
            int: Number of found rows
        """

    def count_by_filters(
        self,
        *,
        filters: IFilterSeq,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> int:
        """
        Count rows by filters

        Args:
            filters (IFilterSeq): Filter sequence
            extra (Extra | None, optional): Extra params.
                Defaults to None
            session (TSession | None): Session to use for DB queries.
                Defaults to None.
                Currently supported for SQLAlchemy

        Returns:
            int: Number of found rows
        """


class operator(IntEnum):
    eq = 0
    lt = 1
    le = 2
    gt = 3
    ge = 4
    in_ = 5
    is_ = 6


class mode(IntEnum):
    and_ = 0
    or_ = 1


@runtime_checkable
class IFilter(Protocol[TTable, TColumn, TFieldValue]):  # type:ignore[misc]
    column: TColumn
    column_name: str
    value: TFieldValue | None
    operator_: operator

    def __init__(
        self,
        table_class: Type[TTable],
        column_name: str,
        value: TFieldValue | None = None,
        operator_: operator = operator.eq,
    ) -> None:
        """
        Args:
            table_class (Type[TTable]): ORM model class
            column_name (str): Name of the column
            value (TFieldValue | None, optional): Value to filter against.
                Defaults to None. Can be set later via __call__
            operator_ (operator | None, optional): Operator for filtering.
                Defaults to operator.eq. Can be set later via __call__
        """

    def __call__(
        self,
        value: TFieldValue,
        operator_: operator = operator.eq,
    ) -> IFilter:
        """
        Finish construction of the object.
        This is a 2nd-step construction for DI support

        Args:
            value (TFieldValue): Value to filter against
            operator_ (operator, optional): Operator for filtering.
                Defaults to operator.eq

        Returns:
            IFilter: Completed filter object

        Examples:
            ```
            uuid_filter = Filter(File, "uuid")([str(uuid4()), str(uuid4())], operator.in_)  # noqa:E501
            ```
        """


class IFilterSeq(Protocol[TCompiledFilter]):
    def __init__(
        self,
        /,
        mode_: mode,
        *filters: IFilter | IFilterSeq[TCompiledFilter],
    ) -> None:
        """
        Args:
            mode_ (mode): Condition type between passed filters

        Examples:
            1. Multiple filters
            ```
            FilterSeq(mode.and_, uuid_filter("uuid"), path_filter("path"))
            ```
            2. Filter + Sequence
            ```
            filter_seq = FilterSeq(mode.and_, uuid_filter("uuid"), path_filter("path"))
            FilterSeq(mode.or_, created_at_filter(now), filter_seq)
            ```
            3. Sequences
            ```
            filter_seq_1 = FilterSeq(mode.and_, uuid_filter("uuid1"), path_filter("path1"))  # noqa:E501
            filter_seq_2 = FilterSeq(mode.and_, uuid_filter("uuid2"), path_filter("path2"))  # noqa:E501
            FilterSeq(mode.or_, filter_seq_1, filter_seq_2)
            ```
        """

    def compile(self) -> TCompiledFilter:
        """
        Returns:
            TCompiledFilter: Compiled filter for usage in orm
        """
