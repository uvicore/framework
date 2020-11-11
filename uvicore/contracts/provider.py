from abc import ABC, abstractmethod
from typing import Any, Dict, List

from uvicore.contracts import Application, Package, Dispatcher


class Provider(ABC):

    @property
    @abstractmethod
    def app(self) -> Application:
        """Uvicore application instance"""
        pass

    @property
    @abstractmethod
    def events(self) -> Dispatcher:
        """Event instance"""
        pass

    @property
    @abstractmethod
    def package(self) -> Package:
        """The current package class.  Not available in boot()"""
        pass

    @property
    @abstractmethod
    def app_config(self) -> Dict: pass

    @property
    @abstractmethod
    def package_config(self) -> Dict: pass

    @property
    def name(self) -> Dict: pass

    @abstractmethod
    def register(self) -> None: pass

    @abstractmethod
    def boot(self) -> None: pass

    @abstractmethod
    def bind(self,
        name: str,
        object: Any,
        *,
        factory: Any = None,
        kwargs: Dict = None,
        singleton: bool = False,
        aliases: List = []
    ) -> None:
        """Bind a concrete class to an IoC name"""
        pass

    @abstractmethod
    def views(self, package: Package, paths: List) -> None:
        """Register packages view paths"""
        pass

    @abstractmethod
    def assets(self, package: Package, paths: List) -> None:
        """Register packages asset paths"""
        pass

    @abstractmethod
    def template(self, package: Package, options: Dict) -> None:
        """Register packages view templating options"""
        pass

    @abstractmethod
    def web_routes(self, package: Package, routes_class: Any) -> None:
        """Register packages web routes"""
        pass

    @abstractmethod
    def api_routes(self, package: Package, routes_class: Any) -> None:
        """Register packages API routes"""
        pass

    @abstractmethod
    def models(self, models: List[str]) -> None:
        """Register packages database ORM models"""
        pass

    @abstractmethod
    def tables(self, tables: List[str]) -> None:
        """Register packages database tables"""
        pass

    @abstractmethod
    def seeders(self, seeders: List[str]) -> None:
        """Register packages database seeders"""
        pass

    @abstractmethod
    def commands(self, package: Package, options: Dict) -> None:
        """Register packages CLI commands"""
        pass

    @abstractmethod
    def configs(self, modules: List) -> None:
        """Register packages configs"""
        pass
