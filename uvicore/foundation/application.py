import os
import sys
import uvicore
from uvicore.typing import Any, List, NamedTuple, Tuple, Dict, OrderedDict, Union
from uvicore.package import Package
from uvicore.contracts import Application as ApplicationInterface
from uvicore.contracts import Config as ConfigInterface
from uvicore.contracts import Package as PackageInterface
from uvicore.contracts import Server as ServerInterface
from uvicore.contracts import Template as TemplateInterface
from uvicore.support.collection import dotget
from uvicore.support.dumper import dd, dump
from uvicore.support.hash import md5
from uvicore.support.module import load, location
from uvicore.console import command_is

#import uvicore.foundation.events.app
from uvicore.foundation.events import app as events

try:
    from fastapi import FastAPI
    from starlette.applications import Starlette
except ImportError:  # pragma: nocover
    FastAPI = None  # type: ignore
    Starlette = None  # type: ignore


@uvicore.service('uvicore.foundation.application.Application',
    aliases=['Application', 'application', 'App', 'app'],
    singleton=True,
)
class Application(ApplicationInterface):
    """Application private class.

    Do not import from this location.
    Use the uvicore.app singleton global instead."""

    # Instance Variables
    @property
    def version(self) -> str:
        return self._version

    @property
    def debug(self) -> bool:
        return self._debug

    @property
    def perfs(self) -> List:
        return self._perfs

    @property
    def http(self) -> Union[Starlette, FastAPI]:
        return self._http

    # No, don't want duplicate entrypoints
    # @property
    # def config(self) -> ConfigInterface:
    #     return self._config

    @property
    def providers(self) -> OrderedDict[str, Dict]:
        return self._providers

    @property
    def registered(self) -> bool:
        return self._registered

    @property
    def booted(self) -> bool:
        return self._booted

    @property
    def is_console(self) -> bool:
        return self._is_console

    @property
    def is_http(self) -> bool:
        return self._is_http

    @property
    def packages(self) -> OrderedDict[str, PackageInterface]:
        return self._packages

    @property
    def running_config(self) -> OrderedDict:
        return self._running_config

    @property
    def path(self) -> str:
        return self._path

    @property
    def name(self) -> str:
        return self._name

    @property
    def main(self) -> Dict:
        return self._main


    def __init__(self):
        # Instance variables
        self._version = uvicore.__version__
        self._debug = False
        self._perfs = []
        self._http = None
        #self._config = None  # None until config provider registered
        self._providers = OrderedDict()
        self._registered = False
        self._booted = False
        self._is_console = False
        self._is_http = False
        self._packages = OrderedDict()
        self._running_config = OrderedDict()
        self._path = None
        self._name = None
        self._main = None


    def add_running_config(self, key: str, value):
        if type(value) == list:
            if not self._running_config.dotget(key): self._running_config.dotset(key, [])
            self._running_config.dotget(key).extend(value)
        else:
            self._running_config.dotset(key, value)


    def bootstrap(self, app_config: Dict, path: str, is_console: bool) -> None:
        """Bootstrap the uvicore application"""

        # Silently do not bootstrap multiple times
        if self.booted: return

        # App name and path
        self._path = path
        self._name = app_config.name
        self._main = app_config.main

        # Add to running config
        self.add_running_config('name', self.name)
        self.add_running_config('main', self.main)
        self.add_running_config('path', self.path)
        self.add_running_config('version', '0.0.0') # Fill in later from main running package config
        self.add_running_config('uvicore_version', self.version)

        # Detect if running in console (to register commands)
        # Ensure console is False even when running ./uvicore http serve
        self._is_console = is_console
        if command_is('http serve'): self._is_console = False
        self._is_http = not self.is_console

        # Detect debug flag from main app config
        self._debug = app_config.debug
        self.add_running_config('debug', self.debug)

        # Build recursive providers graph
        self._build_provider_graph(app_config)
        #self.add_running_config('providers', self.providers)

        # Failsafe if no http package, force console
        # This solves a ./uvicore http serve error if you don't have the http package
        #if 'uvicore.web' not in self.providers or 'uvicore.api' not in self.providers:
        if 'uvicore.http' not in self.providers:
            self._is_console = True
            self._is_http = False

        # Register all providers by calling each packages register() method
        # This is what builds self._packages with an actual Package Class objects
        # Uses self.providers and converts those into full Package objects
        self._register_providers(app_config)

        # Boot all providers by calling each packages boot() method
        self._boot_providers(app_config)

        # Add each final package to running_config, but only the basic details
        # self.add_running_config('packages', self.packages)
        for package in self.packages.values():
            if package.main:
                self.add_running_config('version', package.version)
            self.add_running_config('packages.[' + package.name + ']', {
                'name': package.name,
                'short_name': package.short_name,
                'vendor': package.vendor,
                'version': package.version,
                'main': package.main,
                'path': package.path,
                'registers': [k for (k,v) in package.registers.items() if v == True],
            })

        # Return application
        return self


    def package(self, package: str = None, *, main: bool = False, hint: str = None) -> PackageInterface:
        """Get package by name or by main running package"""
        if package:
            return self.packages.get(package)
            #return self.packages.dotget(package)
        elif main:
            return next(package for package in self.packages.values() if package.main == True)
        elif hint:
            return self.package('app1')
            #return self.packages.dotget(self.main)


    def perf(self, item) -> None:
        """Add entry to debug performance counter"""
        if self.debug:
            self.perfs.append(item)
            print(item)


    def _build_provider_graph(self, app_config: Dict) -> None:
        """Build recursive dependency graph of all packages"""

        def recurse(package: str, options: Dict):
            # Get the config/package.py config
            package_config = self._get_package_config(package, options)

            # Get the packages service provider dependencies
            services = package_config.get('dependencies') or {}

            # Recurse into each service dependency and find those dependencies from their config/package.py configs
            for service, details in services.items():
                recurse(service, details)

            # Add to providers OrderedDict. Notice this will OVERWRITE if new provider defined last.
            # This gives the perfect LAST provider WINS!  Also because this is an OrderedDict the
            # last provider will overrite the value but the defined ORDER will remain the
            # same.  Perfect!
            self._providers[package] = options

        # Graph starts with "main", this is the package acting as the main running app itself
        main = app_config.main
        if 'config' in main:
            # Allows main to specific a custom config location
            recurse(main.package, {
                'provider': main.provider,
                'config': main.config
            })
        else:
            recurse(main.package, {
                'provider': main.provider,
            })

        # Next we loop all app defined overrides.providers
        overrides = app_config.overrides.providers or {}
        for package, options in overrides.items():
            recurse(package, options)


    def _register_providers(self, app_config: Dict) -> None:
        """Register all providers by calling each ServiceProviders register() method"""

        for package_name, service in self.providers.items():
            # Example:
            # package_name = uvicore.configuration
            # service = {
            #   'provider': 'uvicore.configuration.services.Configuration',
            #   'config': 'uvicore.configuration.config.package.config',
            # }

            # Get the config/package.py config
            package_config = self._get_package_config(package_name, service)

            # Start a new package definition
            self._packages[package_name] = Package({
                'name': package_name,
                'short_name': package_name.split('.')[-1] if '.' in package_name else package_name,
                'vendor': package_name.split('.')[0],  # Works fine even if no .
                'version': package_config.version or '0.1.0',
                'main': True if package_name == self.main.package else False,
                'path': location(package_name),
            })

            # Instantiate the provider and call the register() method
            provider = load(service['provider']).object(
                app=self,
                name=package_name,
                package=None,  # Not available in register()
                app_config=app_config,
                package_config=package_config,
            )
            provider.register()

        # Complete registration
        self._registered = True
        #uvicore.events.dispatch('uvicore.foundation.events.app.Registered')
        #uvicore.events.dispatch(uvicore.foundation.events.app.Registered())
        #uvicore.events.dispatch('uvicore.foundation.events.app.Registered', {'test': 'test1'})
        events.Registered().dispatch()


    def _boot_providers(self, app_config: Dict) -> None:
        for package_name, service in self.providers.items():

            # Example:
            # package_name = uvicore.configuration
            # service = {'provider': 'uvicore.configuration.services.Configuration'}

            # Get the config/package.py config
            package_config = self._get_package_config(package_name, service)

            # Import the provider and call boot()
            provider = load(service['provider']).object(
                app=self,
                name=package_name,
                package=self.package(package_name),
                app_config=app_config,
                package_config=package_config,
            )
            provider.boot()

        # Complete booting
        self._booted = True
        #uvicore.events.dispatch('uvicore.foundation.events.app.Booted')
        #uvicore.events.dispatch(uvicore.foundation.events.app.Booted())
        #uvicore.events.dispatch('uvicore.foundation.events.app.Booted')
        events.Booted().dispatch()

    def _get_package_config(self, package: str, options: Dict) -> Dict:
        """Load packages configuration"""
        config_module = package + '.config.package.config'  # Default if not defined
        if 'config' in options: config_module = options['config']
        config = Dict()
        try:
            config = Dict(load(config_module).object)
        except:
            # Often we won't have any config for a package, if so return empty Dict
            pass
        return config

    # NO, don't want duplicates of everything everywhere, just import dumper
    # def dump(self, *args) -> None:
    #     dump(*args)

    # def dd(self, *args) -> None:
    #     dd(*args)


# IoC Class Instance
# **Not meant to be imported from here**.  Use the uvicore.app singleton global instead.
# Only here because uvicore bootstrap needs to import it without a service provider.
# By using the default bind and make feature of the IoC we can swap the implimentation
# at a high bootstrap level using our app configs 'bindings' dictionary.
# The only two classes that do this are Application and the event Dispatcher.
#Application: _Application = uvicore.ioc.make('Application', _Application, singleton=True, aliases=['App', 'app', 'application'])
