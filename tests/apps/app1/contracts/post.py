from __future__ import annotations
from typing import Optional, List
from uvicore.contracts import Model as ModelInterface


# Model interfaces, though redundant, are used for proper type hinting code intellisense
class Post(ModelInterface):
    id: Optional[int]
    slug: str
    title: str
    other: str
    cb: str
    creator_id: int
    creator: Optional[User]
    creator2: Optional[User]
    comments: Optional[List[Comment]]
    tags: Optional[List[Tag]]


# Import relations after model to avoid circular dependencies
from .user import User
from .comment import Comment
from .tag import Tag
