#from __future__ import annotations
from abc import ABC, abstractmethod, abstractclassmethod
from typing import Optional, List, Generic, TypeVar
from uvicore.contracts import OrmQueryBuilder

E = TypeVar("E")

class AutoApi(Generic[E], ABC):

    @classmethod
    def listsig(request,
        include: Optional[List[str]],
        where: Optional[str] = '',
    ) -> None:
        """AutoApi List Multiple Function Signature"""

    @abstractmethod
    def getsig(request,
        include: Optional[List[str]],
    ) -> None:
        """AutoApi Get One Function Signature"""

    @abstractmethod
    def orm_query(self) -> OrmQueryBuilder[OrmQueryBuilder, E]:
        """Start a new Uvicore ORM Model QueryBuilder Query"""
