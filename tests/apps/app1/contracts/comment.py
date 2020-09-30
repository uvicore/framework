from __future__ import annotations
from typing import Optional, List
from uvicore.contracts import Model as ModelInterface


# Model interfaces, though redundant, are used for proper type hinting code intellisense
class Comment(ModelInterface):
    id: Optional[int]
    title: str
    body: str
    post_id: int
    post: Optional[Post]


# Import relations after model to avoid circular dependencies
from .post import Post
