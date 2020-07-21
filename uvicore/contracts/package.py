from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, NamedTuple

from uvicore.database.connection import Connection


@dataclass
class Package(ABC):
    name: str
    vendor: str
    module: str
    location: str
    main: bool
    config_prefix: str
    web_route_prefix: str
    api_route_prefix: str
    view_paths: List[str]
    asset_paths: List[str]
    template_options: Dict
    register_web_routes: bool
    register_api_routes: bool
    register_views: bool
    register_assets: bool
    register_commands: bool
    connections: List[Connection]

    @abstractmethod
    def config(self, dotkey: str = None):
        pass

    @abstractmethod
    def connection(self, name: str = None):
        pass
