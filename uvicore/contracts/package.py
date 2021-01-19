from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, NamedTuple, Any
from .connection import Connection


@dataclass
class Registers(ABC):
    web_routes: bool
    api_routes: bool
    middleware: bool
    views: bool
    assets: bool
    commands: bool
    models: bool
    tables: bool
    seeders: bool


@dataclass
class Package(ABC):
    """asdfasdf"""
    name: str
    location: str
    main: bool
    registers: Registers  # Register (singular) is a reserved word in ABC meta
    web_route_prefix: str
    api_route_prefix: str
    view_paths: List[str]
    asset_paths: List[str]
    template_options: Dict[str, str]
    connection_default: str
    connections: List[Connection]
    #models: List[str]
    seeders: List[str]
    commands: Dict
    config: Dict

    @abstractmethod
    def config(self, dotkey: str = None):
        pass

    @abstractmethod
    def connection(self, name: str = None):
        pass
