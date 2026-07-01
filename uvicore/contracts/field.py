from __future__ import annotations
#from abc import ABC, abstractmethod
from typing import Any, Dict

class Field:
    column: str
    name: str | None
    primary: bool | None
    title: str | None
    description: str | None
    default: Any | None
    sortable: bool | None
    searchable: bool | None
    read_only: bool | None
    write_only: bool | None
    callback: Any | None
    evaluate: Any | None
    relation: Relation | None
    json: bool | None
    properties: Dict | None

    min_length: int | None = None
    max_length: int | None = None
    example: Any | None = None

# At bottom due to circular issues between these two contracts
from .relation import Relation  # isort:skip
