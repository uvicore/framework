from __future__ import annotations
from abc import ABC, abstractmethod, abstractproperty
from uvicore.typing import List, Dict, Callable, TypeVar, Generic, Decorator, Optional, Any, Union

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
    prefix: bool
    endpoint: Callable
    methods: List[str]
    response_model: Optional[Any]
    response_class: Optional[Any]
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

    @abstractmethod
    def controller(self,
        module: Union[str, Callable],
        *,
        prefix: str = '',
        name: str = '',
        tags: Optional[List[str]] = None,
        options: Dict = {}
    ) -> List:
        """Include a Route Controller"""

    @abstractmethod
    def include(self,
        module: Union[str, Callable],
        *,
        prefix: str = '',
        name: str = '',
        tags: Optional[List[str]] = None,
        options: Dict = {}
    ) -> List:
        """Alias to controller"""

    @abstractmethod
    def group(self, prefix: str = '', *,
        routes: Optional[List] = None,
        name: str = '',
        tags: Optional[List[str]] = None,
        autoprefix: bool = True,
        middleware: Optional[List] = None,
        auth: Optional[Any] = None,
        scopes: Optional[List] = None,
    ) -> Callable[[Decorator], Decorator]:
        """Route groups method and decorator"""

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
