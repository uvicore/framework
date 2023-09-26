from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from .connection import Connection
from uvicore.typing import Dict, List, Any
from prettyprinter import pretty_call, register_pretty


class Package(Dict):
    """Package Definition"""

    # These class level properties are for type annotations only.
    # They do not restrict of define valid properties like a dataclass would.
    # This is still a fully dynamic SuperDict!
    name: str
    short_name: str
    vendor: str
    version: str
    main: bool
    path: str
    paths: Dict
    registers: Dict
    database: _Database
    web: _Web
    api: _Api
    console: _Console

    @abstractmethod
    def config(self, dotkey: str = None) -> Dict:
        """Helper to access this packages configs"""
        pass

    @abstractmethod
    def connection(self, name: str = None) -> Connection:
        """Helper to access this packages connections"""
        pass


class _Database(Dict):
    """Simple Package Database Type Annotations for the SuperDict"""
    connections: List[Connection]
    connection_default: str
    models: List[str]
    tables: List[str]
    seeders: List[str]


class _Web(Dict):
    prefix: str
    routes_module: str
    routes: Dict[str, WebRoute]
    view_paths: List[str]
    asset_paths: List[str]
    template_options: Dict

class _Api(Dict):
    prefix: str
    routes_files: str
    routes: Dict[str, ApiRoute]


class _Http(Dict):
    """Simple Package HTTP Type Annotations for the SuperDict"""
    web_routes: List[str]
    api_routes: List[str]
    web_route_prefix: str
    api_route_prefix: str
    middleware: List[str]
    view_paths: List[str]
    asset_paths: List[str]
    template_options: Dict



class _Console:
    """Simple Package Console Type Annotations for the SuperDict"""
    groups: Dict


# Bottom to avoid circular dependencies
from .router import WebRoute, ApiRoute  # isort:skip



# @dataclass
# class Package_OBSOLETE_NOW_DIC(ABC):
#     """asdfasdf"""
#     name: str
#     location: str
#     main: bool
#     #registers: Registers  # Register (singular) is a reserved word in ABC meta
#     web_route_prefix: str
#     api_route_prefix: str
#     view_paths: List[str]
#     asset_paths: List[str]
#     template_options: Dict[str, str]
#     connection_default: str
#     connections: List[Connection]
#     #models: List[str]
#     seeders: List[str]
#     commands: Dict
#     config: Dict

#     @abstractmethod
#     def config(self, dotkey: str = None) -> Any:
#         pass

#     @abstractmethod
#     def connection(self, name: str = None) -> Connection:
#         pass



@register_pretty(Package)
def pretty_entity(value, ctx):
    """Custom pretty printer for my SuperDict"""
    # This printer removes the class name uvicore.types.Dict and makes it print
    # with a regular {.  This really cleans up the output!

    # SuperDict are printed as Dict, but this Package SuperDict should
    # be printed more like a class with key=value notation, so use **values
    return pretty_call(ctx, 'Package', **value)
