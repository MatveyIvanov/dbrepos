from dataclasses import dataclass


@dataclass
class InsertTableEntity:
    name: str
    is_deleted: bool


@dataclass
class TableEntity:
    id: int
    name: str
    is_deleted: bool
