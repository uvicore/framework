import uvicore
from typing import Dict
from uvicore.package import Package
from uvicore.support.module import location
from uvicore.support.dumper import dump
from uvicore.support.collection import dotget

# Pull original from Ioc
Base = uvicore.ioc.make('uvicore.foundation.application.Application_BASE')

# ALL BROKEN and disabled in config now that I moved to dynamic package definitions

class Application(Base):
    def _register_providers(self, app_config: Dict) -> None:
        super()._register_providers(app_config)

        for package in self._packages.values():
            package.custom1='custom1 override here!!!'
