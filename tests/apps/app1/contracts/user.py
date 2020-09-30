from __future__ import annotations
from typing import Optional, List
from uvicore.contracts import Model as ModelInterface


# Model interfaces, though redundant, are used for proper type hinting code intellisense
class User(ModelInterface):
    id: Optional[int]
    email: str
    app1_extra: Optional[str]
    contact: Optional[Contact]
    posts: Optional[List[Post]]


# Import relations after model to avoid circular dependencies
from .contact import Contact
from .post import Post
