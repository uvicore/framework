from abc import ABC, abstractmethod
from typing import List, Any, Type, Callable

from starlette.routing import BaseRoute

# class Router(ABC):

#     @abstractmethod
#     def package(self, name: str = None, module: str = None, main: bool = False):
#         pass

class WebRouter(ABC):
    """Router for Web Controllers"""

    @property
    @abstractmethod
    def router(self) -> Any: pass

    @property
    @abstractmethod
    def routes(self) -> List[BaseRoute]: pass

    @property
    @abstractmethod
    def on_startup(self) -> None: pass

    @property
    @abstractmethod
    def on_shutdown(self) -> None: pass

    @abstractmethod
    def get(self,
        path: str,
        name: str = None,
    ) -> Callable: pass

    @abstractmethod
    def include_router(self, router: "WebRouter") -> None: pass


class ApiRouter(ABC):
    """Router for API Endpoints"""

    @property
    @abstractmethod
    def router(self) -> Any: pass

    @property
    @abstractmethod
    def routes(self) -> List[BaseRoute]: pass

    @property
    @abstractmethod
    def on_startup(self) -> None: pass

    @property
    @abstractmethod
    def on_shutdown(self) -> None: pass

    @abstractmethod
    def get(self,
        path: str,
        name: str = None,
        *,
        response_model: Type[Any] = None,
        include_in_schema: bool = True
    ) -> Callable: pass

    @abstractmethod
    def include_router(self, router: "APIRouter") -> None: pass
