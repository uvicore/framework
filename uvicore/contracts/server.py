from abc import ABC, abstractmethod
from typing import Callable, List, Any
from starlette.types import ASGIApp


class Server(ABC):

    @property
    @abstractmethod
    def server(self) -> Any: pass

    @abstractmethod
    def include_router(self, router, *, prefix: str = '', tags: List[str] = None) -> None: pass

    @abstractmethod
    def mount(self, path: str, app: ASGIApp, name: str = None) -> None: pass

    @abstractmethod
    def on_event(self, event_type: str) -> Callable: pass

