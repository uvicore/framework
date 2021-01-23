from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from .connection import Connection
from uvicore.typing import Dict, List, Any


class Package(Dict):
    """Package Definition as a Dynamic Dic"""

    # These class level properties for for type annotations only.
    # They do not restrict of define valid properties like a dataclass would.
    # This is still a fully dynamic SuperDict!
    name: str
    main: bool
    path: str
    registers: Dict
    database: _Database
    http: _Http
    console: _Console

    @abstractmethod
    def config(self, dotkey: str = None) -> Dict:
        """Helper to access this packages configs"""
        pass

    @abstractmethod
    def connection(self, name: str = None) -> Connection:
        """Helper to access this packages connections"""
        pass


class _Database:
    """Simple Package Database Type Annotations for the SuperDict"""
    connections: List[Connection]
    connection_default: str
    models: List[str]
    tables: List[str]
    seeders: List[str]


class _Http:
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
