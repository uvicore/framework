import importlib
import sys
from uvicore.typing import Any, Dict, List, Union, Dict

import uvicore
#import typer_async as typer
from uvicore.contracts import Application, Package
from uvicore.contracts import Provider as ProviderInterface
from uvicore.contracts import Dispatcher
from uvicore.console import group as click_group
from uvicore.support.dumper import dd, dump
from uvicore.support.module import load, location


@uvicore.service(aliases=['PackageProvider', 'Provider'])
class Provider(ProviderInterface):

    # Class variable of all registered click groups from app packages
    # Used to extend an existing group from other packages
    __click_groups__ = {}

    @property
    def app(self) -> Application:
        # """Uvicore application instance"""
        return self._app

    @property
    def events(self) -> Dispatcher:
        # """Event instance"""
        return uvicore.events

    @property
    def package(self) -> Package:
        # """The current package class.  Not available in boot()"""
        return self._package

    @property
    def app_config(self) -> Dict:
        return self._app_config

    @property
    def package_config(self) -> Dict:
        return self._package_config

    @property
    def name(self) -> str:
        return self._name

    def __init__(self, app: Application, name: str, package: Package, app_config: Dict, package_config: Dict) -> None:
        self._app = app
        self._name = name
        self._package = package
        self._app_config = app_config
        self._package_config = package_config

    def bind(self,
        name: str,
        object: Any,
        *,
        object_type: str = 'service',
        override: bool = True,
        factory: Any = None,
        kwargs: Dict = None,
        singleton: bool = False,
        aliases: List = []
    ) -> None:
        """Bind objects to the Ioc"""
        # Get override object from config if exists
        override = self.binding(name)
        object = override or object

        # Bind object to IoC
        uvicore.ioc.bind(name, object, factory=factory, kwargs=kwargs, singleton=singleton, aliases=aliases)

    def bind_override(self, name: str, object: str):
        uvicore.ioc.bind_override(name, object)

    def binding(self, name: str) -> str:
        if self.app_config.get('bindings'):
            return self.app_config.get('bindings').get(name)

    def configs(self, options: List[Dict]) -> None:
        for config in options:
            value = None;
            if 'module' in config:
                # Load module to get actual config value
                value = load(config['module']).object
            elif 'value' in config:
                # Actual config already passed
                value = config['value']

            # Don't use is None, because empty Dict({}) won't be caught, must use if not value
            if not value: continue;

            # If uvicore.config is None (brand new) set to empty Dict() before .merge()
            if uvicore.config is None: uvicore.config = Dict()

            # Merge config value with complete config
            new = Dict()
            new.dotset(config['key'], value)
            uvicore.config.merge(new)

    def registers(self, options: Dict) -> None:
        if options is not None:
            self.package.registers = Dict(options)


# IoC Class Instance
#_ServiceProviderIoc: _ServiceProvider = uvicore.ioc.make('ServiceProvider', _ServiceProvider, aliases=['service', 'provider'])

#class ServiceProvider(_ServiceProviderIoc, ProviderInterface):
#    pass

# Public API for import * and doc gens
#__all__ = ['ServiceProvider', '_ServiceProvider']
