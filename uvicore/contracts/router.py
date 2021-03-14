from __future__ import annotations
from abc import ABC, abstractmethod, abstractproperty
from uvicore.typing import List, Dict, Callable, TypeVar, Generic

# Generic Route (Web or Api)
R = TypeVar('R')

# This is my new custom uvicore router

class WebRoute(Dict):
    """WebRoute superdict definition"""

    # These class level properties for for type annotations only.
    # They do not restrict of define valid properties like a dataclass would.
    # This is still a fully dynamic SuperDict!
    path: str
    name: str
    endpoint: Callable
    methods: List[str]
    middleware: Optional[List]
    original_path: str
    original_name: str


class ApiRoute(Dict):
    """WebRoute superdict definition"""

    # These class level properties for for type annotations only.
    # They do not restrict of define valid properties like a dataclass would.
    # This is still a fully dynamic SuperDict!
    path: str
    name: str
    endpoint: Callable
    methods: List[str]
    response_model: Optional[Any]
    tags: Optional[List]
    middleware: Optional[List]
    summary: Optional[str]
    description: Optional[str]
    original_path: str
    original_name: str


class Routes(ABC):
    """Routes and Controller Class"""

    middleware = None
    auth = None
    scopes = None

    @abstractproperty
    def package(self) -> Package: pass


class Router(Generic[R], ABC):
    """Abstract base router class for Web and Api Router Implimentations"""

    @abstractproperty
    def package(self) -> Package: pass

    @abstractproperty
    def routes(self) -> Dict[str, R]: pass


class WebRouter(ABC):
    # Fixme, add get, post, put...
    pass


class ApiRouter(ABC):
    # Fixme, add get, post, put...
    pass


class ModelRouter(ABC):
    # Fixme, add get, post, put...
    pass


# Bottom to avoid circular dependencies
from .package import Package  # isort:skip

















# These were old, for fastapi and starlettee direct

# class WebRouter(ABC):
#     """Router for Web Controllers"""

#     @property
#     @abstractmethod
#     def router(self) -> Any: pass

#     @property
#     @abstractmethod
#     def routes(self) -> List[BaseRoute]: pass

#     @property
#     @abstractmethod
#     def on_startup(self) -> None: pass

#     @property
#     @abstractmethod
#     def on_shutdown(self) -> None: pass

#     @abstractmethod
#     def get(self,
#         path: str,
#         name: str = None,
#     ) -> Callable: pass

#     @abstractmethod
#     def include_router(self, router: "WebRouter") -> None: pass


# class ApiRouter(ABC):
#     """Router for API Endpoints"""

#     @property
#     @abstractmethod
#     def router(self) -> Any: pass

#     @property
#     @abstractmethod
#     def routes(self) -> List[BaseRoute]: pass

#     @property
#     @abstractmethod
#     def on_startup(self) -> None: pass

#     @property
#     @abstractmethod
#     def on_shutdown(self) -> None: pass

#     @abstractmethod
#     def get(self,
#         path: str,
#         name: str = None,
#         *,
#         response_model: Type[Any] = None,
#         include_in_schema: bool = True
#     ) -> Callable: pass

#     @abstractmethod
#     def include_router(self, router: "APIRouter") -> None: pass
