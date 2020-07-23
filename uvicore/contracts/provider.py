from abc import ABC, abstractmethod
from uvicore.contracts import Package
from typing import List, Dict, Any


class Provider(ABC):

    @abstractmethod
    def register(self, app) -> None: pass

    @abstractmethod
    def boot(self, app, package) -> None: pass

    @abstractmethod
    def bind(self,
        name: str,
        object: Any,
        *,
        factory: Any = None,
        kwargs: Dict = None,
        singleton: bool = False,
        aliases: List = []
    ) -> None: pass

    @abstractmethod
    def views(self, package: Package, paths: List) -> None: pass

    @abstractmethod
    def assets(self, package: Package, paths: List) -> None: pass

    @abstractmethod
    def template(self, package: Package, options: Dict) -> None: pass

    @abstractmethod
    def web_routes(self, package: Package, routes_class: Any) -> None: pass

    @abstractmethod
    def api_routes(self, package: Package, routes_class: Any) -> None: pass

    @abstractmethod
    def commands(self, package: Package, options: Dict) -> None: pass

    @abstractmethod
    def configs(self, modules: List) -> None: pass


