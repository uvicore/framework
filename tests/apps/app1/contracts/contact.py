from __future__ import annotations
from typing import Optional, List
from uvicore.contracts import Model as ModelInterface


# Model interfaces, though redundant, are used for proper type hinting code intellisense
class Contact(ModelInterface):
    id: Optional[int]
    name: str
    title: str
    address: str
    phone: str
    user_id: int
    user: Optional[User]


# Import relations after model to avoid circular dependencies
from .user import User
