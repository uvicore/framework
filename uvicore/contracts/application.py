from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple

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
    # Class Variables
    booted: bool
    instantiated: List

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
    def template(self) -> Template:
        """HTML Templating System"""
        pass

    @property
    @abstractmethod
    def cli(self) -> Any:
        """Main click command group"""
        pass

    @property
    @abstractmethod
    def db(self) -> Any:
        """Database instance"""
        pass

    @property
    @abstractmethod
    def config(self) -> Config:
        """Configuration system"""
        pass

    @property
    @abstractmethod
    def providers(self) -> List[Tuple]:
        """List of providers defined in all packages"""
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
    def is_async(self) -> bool:
        """App running in async mode (HTTP).  CLI is not async"""
        pass

    @property
    @abstractmethod
    def packages(self) -> List:
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
    def vendor(self) -> str:
        """Vendor of running application"""
        pass

    @property
    @abstractmethod
    def module(self) -> str:
        """Full module path of running application"""
        pass

    @abstractmethod
    def bootstrap(self, app_config: Dict, path: str, is_console: bool) -> None:
        """Bootstrap the uvicore application

        * Set globals and framework options attributes
        * Register, boot and merge all providers and configs
        * Fire up the CLI instance (only if running CLI commands)
        * Fire up the HTTP server (only if running as a server)
        * Fire up the Database engine
        * Configure template environment and mount static routes
        """
        pass

    @abstractmethod
    def package(self, name: str = None, module: str = None, main: bool = False) -> Package: pass

    @abstractmethod
    def perf(self, item: any) -> None: pass

    @abstractmethod
    def dump(self, *args) -> None: pass

    @abstractmethod
    def dd(self, *args) -> None: pass
