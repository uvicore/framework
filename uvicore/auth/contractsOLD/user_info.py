from __future__ import annotations
from uvicore.contracts import Model as ModelInterface


# Model interfaces, though redundant, are used for proper type hinting code intellisense
class UserInfo(ModelInterface):
    id: int | None
    extra1: str
    user_id: int
    user: User | None


# Import relations after model to avoid circular dependencies
from .user import User

