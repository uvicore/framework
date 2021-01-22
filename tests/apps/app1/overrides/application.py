import uvicore
from typing import Dict
from uvicore.package import Package
from uvicore.support.module import location
from uvicore.support.dumper import dump
from uvicore.support.collection import dotget

# Pull original from Ioc
Base = uvicore.ioc.make('uvicore.foundation.application._Application_BASE')

# ALL BROKEN and disabled in config now that I moved to dynamic package definitions

class Application(Base):
    def _build_package(self, name: str, custom_config: Dict):
        return Package(
            name=name,
            location=location(name),
            main=True if name == self.main else False,
            web_route_prefix=dotget(custom_config, 'route.web_prefix'),
            api_route_prefix=dotget(custom_config, 'route.api_prefix'),
            view_paths=[],
            asset_paths=[],
            template_options={},
            register_web_routes=custom_config.get('register_web_routes') or True,
            register_api_routes=custom_config.get('register_api_routes') or True,
            register_views=custom_config.get('register_views') or True,
            register_assets=custom_config.get('register_assets') or True,
            register_commands=custom_config.get('register_commands') or True,
            connection_default=dotget(custom_config, 'database.default'),
            connections=self._build_package_connections(custom_config),
            models=[],
            seeders=[],
            custom1='custom1 override here!!!'
        )
