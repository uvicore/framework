from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, NamedTuple
from .connection import Connection


@dataclass
class Package(ABC):
    """asdfasdf"""
    name: str
    location: str
    main: bool
    web_route_prefix: str
    api_route_prefix: str
    view_paths: List[str]
    asset_paths: List[str]
    template_options: Dict[str, str]
    register_web_routes: bool
    register_api_routes: bool
    register_views: bool
    register_assets: bool
    register_commands: bool
    connection_default: str
    connections: List[Connection]
    models: List[str]
    seeders: List[str]

    @abstractmethod
    def config(self, dotkey: str = None):
        pass

    @abstractmethod
    def connection(self, name: str = None):
        pass
