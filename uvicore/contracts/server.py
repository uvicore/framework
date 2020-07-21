from abc import ABC, abstractmethod
from typing import Callable, List

class Server(ABC):

    @property
    @abstractmethod
    def server(self): pass

    @abstractmethod
    def include_router(self, router, *, prefix: str = '', tags: List[str] = None): pass

    @abstractmethod
    def on_event(self, event_type: str) -> Callable: pass

