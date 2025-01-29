from abc import ABC, abstractmethod, abstractproperty
from uvicore.typing import Any, Dict, List, Tuple, OrderedDict, Union
from .config import Config
#from .server import Server
from .package import Package
from .template import Template

try:
    from fastapi import FastAPI
    from starlette.applications import Starlette
except ImportError:  # pragma: nocover
    FastAPI = None  # type: ignore
    Starlette = None  # type: ignore

# Regular attributes (version: str = '0.0.0) vs
# @property @abstractmethod

# Defining attributes here does MAKE the attributes in the
# inheriting class implicitly.  But we don't really want that
# because the user now accept the abstrac classes defaults
# and is not forced to impliment them at all.  We want to FORCE
# the implimentation to define their own attribute values.

# So @property @abstractmethod is the best way to enforce
# requirements and conformity.

class Application(ABC):
    """Main uvicore application"""

    # Instance Variables
    @abstractproperty
    def version(self) -> str:
        """Uvicore framework version number"""
        pass

    @abstractproperty
    def debug(self) -> bool:
        """Debug mode for entire application"""
        pass

    @abstractproperty
    def perfs(self) -> List:
        """List of all perf dumps for performance tuning"""
        pass

    @abstractproperty
    def http(self) -> Union[Starlette, FastAPI]:
        """HTTP Server Instance"""
        pass

    # @property
    # @abstractmethod
    # def config(self) -> Config:
    #     """Configuration system"""
    #     pass

    @abstractproperty
    def providers(self) -> OrderedDict[str, Dict]:
        """OrderedDict of providers from all packages in proper dependency order"""
        pass

    @abstractproperty
    def registered(self) -> bool:
        """All providers have been registered"""
        pass

    @abstractproperty
    def booted(self) -> bool:
        """All providers have been booted"""
        pass

    @abstractproperty
    def is_console(self) -> bool:
        """App running from CLI (not serving web or API)"""
        pass

    @abstractproperty
    def is_http(self) -> bool:
        """App running as HTTP server (not as CLI)"""
        pass

    @abstractproperty
    def packages(self) -> Dict[str, Package]:
        """OrderedDict of all packages defined from providers"""
        pass

    @abstractproperty
    def path(self) -> str:
        """Base path of running application"""
        pass

    @abstractproperty
    def name(self) -> str:
        """Short name of running application"""
        pass

    @abstractproperty
    def main(self) -> str:
        """The main packages running this application"""
        pass

    @abstractmethod
    def bootstrap(self, app_config: Dict, path: str, is_console: bool) -> None:
        """Bootstrap the uvicore application"""
        pass

    @abstractmethod
    def package(self, package: str, *, name: str = None, main: bool = False) -> Package:
        """Get package by name or by main running package"""
        pass

    @abstractmethod
    def perf(self, item: any) -> None:
        """Add entry to debug performance counter"""
        pass

    # @abstractmethod
    # def dump(self, *args) -> None:
    #     """Pretty print args to console"""
    #     pass

    # @abstractmethod
    # def dd(self, *args) -> None:
    #     """Pretty print args to console and exit()"""
    #     pass
