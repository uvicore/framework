import os
import sys
import collections
from typing import Dict, List, NamedTuple, OrderedDict, Tuple, Any

import uvicore
from uvicore import config
#from uvicore.configuration import Config
from uvicore.contracts import Application as ApplicationInterface
from uvicore.contracts import Server as ServerInterface
from uvicore.contracts import Config as ConfigInterface
from uvicore.contracts import Package as PackageInterface
from uvicore.contracts import Template as TemplateInterface
from uvicore.support.dumper import dd, dump
from uvicore.support.module import load, location
from .package import Package

from ..database.connection import Connection
#from uvicore.console import cli as MainClickGroup
#from uvicore.logging.logger import Logger


class _Application(ApplicationInterface):

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
    def http(self) -> ServerInterface:
        return self._http

    @property
    def template(self) -> TemplateInterface:
        return self._template

    @property
    def db(self) -> Any:
        return self._db

    @property
    def config(self) -> ConfigInterface:
        return self._config

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
    def is_async(self) -> bool:
        return self._is_async

    @property
    def packages(self) -> OrderedDict[str, PackageInterface]:
        return self._packages

    @property
    def path(self) -> str:
        return self._path

    @property
    def name(self) -> str:
        return self._name

    @property
    def main(self) -> str:
        return self._main

    def __init__(self):
        # Instance variables
        self._version = uvicore.__version__
        self._debug = False
        self._perfs = []
        self._http = None
        self._template = None
        self._db = None
        self._config = None
        self._providers = collections.OrderedDict()
        self._registered = False
        self._booted = False
        self._is_console = False
        self._is_http = False
        self._is_async = False
        self._packages = collections.OrderedDict()
        self._path = None
        self._name = None
        self._main = None

    def bootstrap(self, app_config: Dict, path: str, is_console: bool) -> None:
        # Silently do not bootstrap multiple times
        if self.booted: return

        # App name and path
        self._path = path
        self._name = app_config.get('name')
        self._main = app_config.get('main')

        # Detect if running in console (to register commands)
        # Ensure console is False even when running ./uvicore http serve
        self._is_console = is_console
        if "'http', 'serve'" in str(sys.argv):
            self._is_console = False
        self._is_http = not self.is_console

        # Detect debug flag from main app config
        self._debug = app_config['debug']

        # Perf
        self.perf('|-foundation.application.bootstrap()')
        self.perf('|--is_console: ' + str(self.is_console))

        # Build recursive providers graph
        self._build_provider_graph(app_config)

        # Register all providers
        self._register_providers(app_config)

        # Merge Providers (merges configs and creates actual Package class)
        self._merge_providers()

        # Create Database instance
        self._create_database_instance()

        # Boot all providers
        #self._boot_providers()
        self._boot_providers(app_config)

        # Return application
        return self

    def _build_provider_graph(self, app_config: Dict) -> None:
        def recurse(package: str, options: Dict):
            package_config = self._get_package_config(package, options)
            services = package_config.get('services') or {}
            for service, details in services.items():
                recurse(service, details)

            # Add to providers, notice this will OVERWRITE if new provider defined
            # This gives the perfect LAST provider WINS!  Also because this is
            # an ordered dict the last provider will overrite the value but the order
            # will remain the same, perfect!
            self._providers[package] = options

        # Loop each main apps packages and recurse into each
        packages = app_config.get('packages') or {}
        for package, options in packages.items():
            recurse(package, options)

    def _register_providers(self, app_config: Dict) -> None:
        self.perf('|--registering providers')
        for package, service in self.providers.items():
            self.perf('|---' + service['provider'])

            # Instantiate the provider and call boot()
            provider = load(service['provider']).object(
                app=self,
                package=None,  # Not available in register()
                app_config=app_config,
                package_config=self._get_package_config(package, service),
            )
            provider.register()

        # Complete registration
        self._registered = True
        uvicore.events.dispatch('uvicore.foundation.events.app.Registered')

    def _merge_providers(self) -> None:
        self.perf('|--merging providers')
        for package, service in self.providers.items():
            self.perf('|---' + service['provider'])

            # Load this packages config/package.py
            package_config = self._get_package_config(package, service)

            # Get this packages config prefix and package name from its configuration
            package_name = package_config.get('name')
            config_prefix = package_name

            # Add in package config with custom config
            self.config.set(config_prefix + '.package', package_config)

            # Load this packages custom config by config_prefix
            custom_config = self.config(config_prefix) or {}

            # Detect if package is running as the actual main app
            main = True if package_name == self.main else False

            # Route prefix
            web_route_prefix = None
            api_route_prefix = None
            if 'route' in custom_config:
                web_route_prefix = custom_config.get('route').get('web_prefix')
                api_route_prefix = custom_config.get('route').get('api_prefix')

            # Database connections
            connections = []
            if 'database' in custom_config:
                for name, connection in custom_config.get('database').get('connections').items():
                    url = (connection.get('driver')
                        + '+' + connection.get('dialect')
                        + '://' + connection.get('username')
                        + ':' + connection.get('password')
                        + '@' + connection.get('host')
                        + ':' + str(connection.get('port'))
                        + '/' + connection.get('database'))
                    #self.db = Database("mysql+pymysql://root:techie@127.0.0.1/uvicore_wiki")
                    connections.append(Connection(
                        name=name,
                        default=True if name == custom_config.get('database').get('default') else False,
                        driver=connection.get('driver'),
                        dialect=connection.get('dialect'),
                        host=connection.get('host'),
                        port=connection.get('port'),
                        database=connection.get('database'),
                        username=connection.get('username'),
                        password=connection.get('password'),
                        prefix=connection.get('prefix'),
                        url=url,
                    ))

            # Modules file path
            package = Package(
                name=package_config.get('name'),
                location=location(package_name),
                main=main,
                web_route_prefix=web_route_prefix,
                api_route_prefix=api_route_prefix,
                view_paths=[],
                asset_paths=[],
                template_options={},
                register_web_routes=True if custom_config.get('register_web_routes') else False,
                register_api_routes=True if custom_config.get('register_api_routes') else False,
                register_views=True if custom_config.get('register_views') else False,
                register_assets=True if custom_config.get('register_assets') else False,
                register_commands=True if custom_config.get('register_commands') else False,
                connections=connections,
            )
            self._packages[package_name] = package

    def _boot_providers(self, app_config: Dict) -> None:
        self.perf('|--booting providers')
        for package, service in self.providers.items():
            self.perf('|---' + service['provider'])

            # Import the provider and call boot()
            provider = load(service['provider']).object(
                app=self,
                package=self.package(package),
                app_config=app_config,
                package_config=self._get_package_config(package, service),
            )
            provider.boot()

        # Complete booting
        self._booted = True
        uvicore.events.dispatch('uvicore.foundation.events.app.Booted')

    def _create_database_instance(self) -> None:
        # Fire up Database
        # if not self.is_console:
        #     # HTTP Async
        #     from databases import Database
        #     self.db = Database("mysql://root:techie@127.0.0.1/uvicore_wiki")
        #     @self.http.on_event("startup")
        #     async def startup():
        #         await self.db.connect()

        #     @self.http.on_event("shutdown")
        #     async def shutdown():
        #         await self.db.disconnect()
        # else:
        # CLI Sync
        from ..database.db import Database
        self._db = Database("mysql+pymysql://root:techie@127.0.0.1/uvicore_wiki")

    def _get_package_config(self, package: str, options: Dict):
        config_module = package + '.config.package.config'  # Default if not defined
        if 'config' in options: config_module = options['config']
        return load(config_module).object

    def package(self, package: str = None, *, main: bool = False) -> PackageInterface:
        if package:
            return self.packages.get(package)
        elif main:
            return next(package for package in self.packages.values() if package.main == True)

    def perf(self, item) -> None:
        if self.debug:
            self.perfs.append(item)
            print(item)

    def dump(self, *args) -> None:
        dump(*args)

    def dd(self, *args) -> None:
        dd(*args)


# Note about Application
# Do not make the main Application class
# or you get an IoC circular dependency issue when you try to override it.
# All other IoC classes work fine, just not the Application.

# IoC Class Instance
# NO - Circular issues on override
# Application: ApplicationInterface = uvicore.ioc.make('Application')

# Public API for import * and doc gens
__all__ = ['_Application']
