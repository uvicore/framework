from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple, OrderedDict

from .config import Config
from .server import Server
from .package import Package
from .template import Template

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
    @property
    @abstractmethod
    def version(self) -> str:
        """Uvicore framework version number"""
        pass

    @property
    @abstractmethod
    def debug(self) -> bool:
        """Debug mode for entire application"""
        pass

    @property
    @abstractmethod
    def perfs(self) -> List:
        """List of all perf dumps for performance tuning"""
        pass

    @property
    @abstractmethod
    def http(self) -> Server:
        """HTTP Server Instance"""
        pass

    @property
    @abstractmethod
    def config(self) -> Config:
        """Configuration system"""
        pass

    @property
    @abstractmethod
    def providers(self) -> OrderedDict[str, Dict]:
        """OrderedDict of providers from all packages in proper dependency order"""
        pass

    @property
    @abstractmethod
    def registered(self) -> bool:
        """All providers have been registered"""
        pass

    @property
    @abstractmethod
    def booted(self) -> bool:
        """All providers have been booted"""
        pass

    @property
    @abstractmethod
    def is_console(self) -> bool:
        """App running from CLI (not serving web or API)"""
        pass

    @property
    @abstractmethod
    def is_http(self) -> bool:
        """App running as HTTP server (not as CLI)"""
        pass

    @property
    @abstractmethod
    def packages(self) -> OrderedDict[str, Package]:
        """List of all packages defined from providers"""
        pass

    @property
    @abstractmethod
    def path(self) -> str:
        """Base path of running application"""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Short name of running application"""
        pass

    @property
    @abstractmethod
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

    @abstractmethod
    def dump(self, *args) -> None:
        """Pretty print args to console"""
        pass

    @abstractmethod
    def dd(self, *args) -> None:
        """Pretty print args to console and exit()"""
        pass
