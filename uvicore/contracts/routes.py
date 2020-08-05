from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, TypeVar

from uvicore.contracts import Application, Package

# Generic Router (APIRouter or WebRouter)
R = TypeVar('R')

class Routes(Generic[R], ABC):

    @property
    @abstractmethod
    def app(self) -> Application: pass

    @property
    @abstractmethod
    def package(self) -> Package: pass

    @property
    @abstractmethod
    def Router(self) -> R: pass

    @property
    @abstractmethod
    def prefix(self) -> str: pass

    @abstractmethod
    def include(self, module, *, prefix: str = '', tags: List[str] = None) -> None:
        """Include a new router object"""
        pass
