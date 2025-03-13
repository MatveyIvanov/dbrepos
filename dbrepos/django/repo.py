from dataclasses import asdict
from typing import TYPE_CHECKING, Iterable, Mapping, Sequence, Tuple, Type, TypeVar

if TYPE_CHECKING:
    from _typeshed import DataclassInstance

from django.db.models import Model, Q, QuerySet  # type:ignore[import-untyped]

from dbrepos.core.abstract import IFilterSeq, IRepo, mode, operator
from dbrepos.core.types import Extra
from dbrepos.decorators import convert as _convert
from dbrepos.decorators import handle_error as _handle_error
from dbrepos.decorators import strict as _strict
from dbrepos.django.filters import DjangoFilter, DjangoFilterSeq
from dbrepos.shortcuts import get_object_or_404 as _get_object_or_404

TTable = TypeVar("TTable", bound=Model)
if TYPE_CHECKING:
    TEntity = TypeVar("TEntity", bound=DataclassInstance, contravariant=True)
    TResultDataclass = TypeVar("TResultDataclass", bound=DataclassInstance)
else:
    TEntity = TypeVar("TEntity")
    TResultDataclass = TypeVar("TResultDataclass")
TResultORM = TypeVar("TResultORM", bound=Model, covariant=True)
TPrimaryKey = TypeVar("TPrimaryKey", int, str, covariant=True)
TFieldValue = TypeVar("TFieldValue")
TSession = TypeVar("TSession", covariant=True)

strict = _strict
handle_error = _handle_error
convert = _convert
get_object_or_404 = _get_object_or_404


class DjangoRepo(IRepo[TTable, TResultORM]):
    def __init__(
        self,
        *,
        table_class: Type[TTable],
        pk_field_name: str = "id",
        is_soft_deletable: bool = False,
        default_ordering: Tuple[str] = ("id",),
    ):
        self.table_class = table_class
        self.pk_field_name = pk_field_name
        self.is_soft_deletable = is_soft_deletable
        self.default_ordering = default_ordering

        assert hasattr(self.table_class, self.pk_field_name), "Wrong pk_field_name"

    @handle_error
    @convert(orm="django")
    def create(
        self,
        entity: TEntity,
        *,
        convert_to: Type[TResultDataclass] | None = None,
        session: TSession | None = None,
    ) -> TResultDataclass | TResultORM:
        return self.table_class.objects.create(**asdict(entity))

    @handle_error
    @strict
    @convert(orm="django")
    def get_by_field(
        self,
        *,
        name: str,
        value: TFieldValue,
        convert_to: Type[TResultDataclass] | None = None,
        strict: bool = True,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> TResultDataclass | TResultORM | None:
        return get_object_or_404(
            self._make_convertable(
                qs=self._resolve_extra(qs=self.table_class.objects, extra=extra).filter(
                    **{name: value}
                ),
                convert_to=convert_to,
            ).first(),
        )

    @handle_error
    @strict
    @convert(orm="django")
    def get_by_filters(
        self,
        *,
        filters: IFilterSeq[Q],
        convert_to: Type[TResultDataclass] | None = None,
        strict: bool = True,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> TResultDataclass | TResultORM | None:
        return get_object_or_404(
            self._make_convertable(
                qs=self._resolve_extra(qs=self.table_class.objects, extra=extra).filter(
                    filters.compile()
                ),
                convert_to=convert_to,
            ).first()
        )

    @handle_error
    def get_by_pk(
        self,
        pk: TPrimaryKey,
        *,
        convert_to: Type[TResultDataclass] | None = None,
        strict: bool = True,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> TResultDataclass | TResultORM | None:
        return self.get_by_field(
            name=self.pk_field_name,
            value=pk,
            strict=strict,
            extra=extra,
            session=session,
            convert_to=convert_to,
        )

    @handle_error
    @convert(many=True, orm="django")
    def all(
        self,
        *,
        convert_to: Type[TResultDataclass] | None = None,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> Iterable[TResultDataclass | TResultORM]:
        return self._make_convertable(
            qs=self._all(extra=extra),
            convert_to=convert_to,
        )

    @handle_error
    @convert(many=True, orm="django")
    def all_by_field(
        self,
        *,
        name: str,
        value: TFieldValue,
        convert_to: Type[TResultDataclass] | None = None,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> Iterable[TResultDataclass | TResultORM]:
        return self._make_convertable(
            qs=self._all_by_field(name=name, value=value, extra=extra),
            convert_to=convert_to,
        )

    @handle_error
    @convert(many=True, orm="django")
    def all_by_filters(
        self,
        *,
        filters: IFilterSeq[Q],
        convert_to: Type[TResultDataclass] | None = None,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> Iterable[TResultDataclass | TResultORM]:
        return self._make_convertable(
            qs=self._all_by_filters(filters=filters, extra=extra),
            convert_to=convert_to,
        )

    @handle_error
    @convert(many=True, orm="django")
    def all_by_pks(
        self,
        pks: Sequence[TPrimaryKey],
        *,
        convert_to: Type[TResultDataclass] | None = None,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> Iterable[TResultDataclass | TResultORM]:
        if not pks:
            return []
        return self._make_convertable(
            qs=self._all_by_pks(pks=pks, extra=extra),
            convert_to=convert_to,
        )

    @handle_error
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
        self._all_by_pks(pks=[pk], extra=extra).update(**values)

    @handle_error
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
        self._all_by_pks(pks=pks, extra=extra).update(**values)

    @handle_error
    def delete(
        self,
        pk: TPrimaryKey,
        *,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> None:
        self._all_by_pks(pks=[pk], extra=extra).delete()

    @handle_error
    def delete_by_field(
        self,
        *,
        name: str,
        value: TFieldValue,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> None:
        self._all_by_field(name=name, value=value, extra=extra).delete()

    @handle_error
    def exists_by_field(
        self,
        *,
        name: str,
        value: TFieldValue,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> bool:
        return self._all_by_field(name=name, value=value, extra=extra).exists()

    @handle_error
    def exists_by_filters(
        self,
        *,
        filters: IFilterSeq,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> bool:
        return self._all_by_filters(filters=filters, extra=extra).exists()

    @handle_error
    def count_by_field(
        self,
        *,
        name: str,
        value: TFieldValue,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> int:
        return self._all_by_field(name=name, value=value, extra=extra).count()

    @handle_error
    def count_by_filters(
        self,
        *,
        filters: IFilterSeq,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> int:
        return self._all_by_filters(filters=filters, extra=extra).count()

    """ Low-level API """

    def _all(
        self,
        *,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> QuerySet[TTable]:
        return self._resolve_extra(qs=self.table_class.objects.all(), extra=extra)

    def _all_by_field(
        self,
        *,
        name: str,
        value: TFieldValue,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> QuerySet[TTable]:
        return self._resolve_extra(
            qs=self.table_class.objects.filter(**{name: value}),
            extra=extra,
        )

    def _all_by_filters(
        self,
        *,
        filters: IFilterSeq[Q],
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> QuerySet[TTable]:
        return self._resolve_extra(
            qs=self.table_class.objects.filter(filters.compile()),
            extra=extra,
        )

    def _all_by_pks(
        self,
        pks: Sequence[TPrimaryKey],
        *,
        extra: Extra | None = None,
        session: TSession | None = None,
    ) -> QuerySet[TTable]:
        return self.all_by_filters(
            filters=DjangoFilterSeq(
                mode.and_,
                DjangoFilter(
                    table_class=self.table_class,
                    column_name=self.pk_field_name,
                    value=pks,
                    operator_=operator.in_,
                ),
            ),
            extra=extra,
        )

    """ Utils """

    def _resolve_extra(
        self,
        *,
        qs: QuerySet[TTable],
        extra: Extra | None,
    ) -> QuerySet[TTable]:
        if not extra:
            extra = Extra()
        qs = qs.order_by(*(extra.ordering or self.default_ordering))
        if extra.for_update:
            qs = qs.select_for_update()
        if self.is_soft_deletable and not extra.include_soft_deleted:
            qs = qs.filter(is_deleted=False)
        if extra.select_related:
            qs = qs.select_related(*extra.select_related)
        return qs

    def _make_convertable(
        self,
        *,
        qs: QuerySet[TTable],
        convert_to: Type[TResultDataclass] | None,
    ) -> QuerySet[TTable]:
        if convert_to is None:
            return qs
        return qs.values_list()
