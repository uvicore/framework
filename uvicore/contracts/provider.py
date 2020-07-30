from abc import ABC, abstractmethod
from typing import Any, Dict, List

from uvicore.contracts import Application, Package


class Provider(ABC):

    @property
    @abstractmethod
    def app(self) -> Application: pass

    @property
    @abstractmethod
    def package(self) -> Package: pass

    @property
    @abstractmethod
    def app_config(self) -> Dict: pass

    @property
    @abstractmethod
    def package_config(self) -> Dict: pass

    @property
    def name(self) -> Dict: pass

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
