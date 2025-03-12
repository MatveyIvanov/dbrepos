from dataclasses import dataclass, field
from enum import IntEnum
from typing import Literal, Tuple

ORM = Literal["django", "alchemy"]


@dataclass
class Extra:
    """
    Args:
        for_update (bool): Lock row.
            Defaults to False
        include_soft_deleted (bool): Include soft deleted rows.
            Works only for soft deletable models.
            Defaults to False
        ordering (Tuple[str]): Result ordering.
            Defaults to empty tuple (meaning default ordering is applied)
        select_related (Tuple[str]): Columns to join from related tables.
            Defaults to empty tuple (meaning columns are joined)
    """

    for_update: bool = False
    include_soft_deleted: bool = False
    ordering: Tuple[str, ...] = field(default_factory=tuple)
    select_related: Tuple[str, ...] = field(default_factory=tuple)


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
