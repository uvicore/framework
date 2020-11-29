from __future__ import annotations
from typing import Optional, List
from uvicore.contracts import Model as ModelInterface


# Model interfaces, though redundant, are used for proper type hinting code intellisense
class Group(ModelInterface):
    id: Optional[int]
    name: str


# Import relations after model to avoid circular dependencies
