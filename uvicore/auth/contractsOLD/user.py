from __future__ import annotations
from uvicore.contracts import Model as ModelInterface


# Model interfaces, though redundant, are used for proper type hinting code intellisense
class User(ModelInterface):
    id: int | None
    email: str
    info: UserInfo | None


# Import relations after model to avoid circular dependencies
from .user_info import UserInfo
