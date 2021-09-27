from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Any, Dict

class Field:
    column: str
    name: Optional[str]
    primary: Optional[bool]
    title: Optional[str]
    description: Optional[str]
    default: Optional[Any]
    sortable: Optional[bool]
    searchable: Optional[bool]
    read_only: Optional[bool]
    write_only: Optional[bool]
    callback: Optional[Any]
    evaluate: Optional[Any]
    relation: Optional[Relation]
    json: Optional[bool]
    properties: Optional[Dict]

    min_length: Optional[int] = None
    max_length: Optional[int] = None
    example: Optional[Any] = None

# At bottom due to circular issues between these two contracts
from .relation import Relation  # isort:skip
