import collections
import os
import sys
from typing import Any, Dict, List, NamedTuple, OrderedDict, Tuple

import uvicore
from uvicore.contracts import Application as ApplicationInterface
from uvicore.contracts import Config as ConfigInterface
from uvicore.contracts import Package as PackageInterface
from uvicore.contracts import Server as ServerInterface
from uvicore.contracts import Template as TemplateInterface
from uvicore.database import Connection
from uvicore.package import Package
from uvicore.support.collection import dotget
from uvicore.support.dumper import dd, dump
from uvicore.support.hash import md5
from uvicore.support.module import load, location


@uvicore.service('uvicore.foundation.application._Application',
    aliases=['Application', 'application', 'App', 'app'],
    singleton=True,
)
class _Application:
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
    def http(self) -> ServerInterface:
        return self._http

    # @property
    # def template(self) -> TemplateInterface:
    #     return self._template

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
        self._config = None  # None until config provider registered
        self._providers = collections.OrderedDict()
        self._registered = False
        self._booted = False
        self._is_console = False
        self._is_http = False
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
        #self._is_async = self.is_http

        # Detect debug flag from main app config
        self._debug = app_config['debug']

        # Perf
        self.perf('|-foundation.application.bootstrap()')
        self.perf('|--is_console: ' + str(self.is_console))

        # Build recursive providers graph
        self._build_provider_graph(app_config)

        # Register and merge all providers
        self._register_providers(app_config)

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

        # Merge all registered configs and create actual packages
        self._merge_providers()

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

            # Build package dataclass and append to all packages
            package = self._build_package(package_name, custom_config)
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
        )

    def _build_package_connections(self, custom_config):
        connections = []
        if 'database' not in custom_config: return []
        if 'connections' not in custom_config['database']: return []
        for name, connection in custom_config['database']['connections'].items():
            # Metakey cannot be the connection name.  If 2 connections share the exact
            # same database (host, port, dbname) then they need to also share the same
            # metedata for foreign keys to work properly.
            if connection.get('driver') == 'sqlite':
                url = 'sqlite:///' + connection.get('database')
                metakey = url
            else:
                url = (connection.get('driver')
                    + '+' + connection.get('dialect')
                    + '://' + connection.get('username')
                    + ':' + connection.get('password')
                    + '@' + connection.get('host')
                    + ':' + str(connection.get('port'))
                    + '/' + connection.get('database')
                )
                metakey = (connection.get('host')
                    + ':' + str(connection.get('port'))
                    + '/' + connection.get('database')
                )

            #self.db = Database("mysql+pymysql://root:techie@127.0.0.1:3306/uvicore_wiki")
            connections.append(Connection(
                name=name,
                #default=True if name == custom_config.get('database').get('default') else False,
                driver=connection.get('driver'),
                dialect=connection.get('dialect'),
                host=connection.get('host'),
                port=connection.get('port'),
                database=connection.get('database'),
                username=connection.get('username'),
                password=connection.get('password'),
                prefix=connection.get('prefix') or '',
                metakey=metakey,
                url=url,
            ))
        return connections

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


# IoC Class Instance
# **Not meant to be imported from here**.  Use the uvicore.app singleton global instead.
# Only here because uvicore bootstrap needs to import it without a service provider.
# By using the default bind and make feature of the IoC we can swap the implimentation
# at a high bootstrap level using our app configs 'bindings' dictionary.
# The only two classes that do this are Application and the event Dispatcher.
#Application: _Application = uvicore.ioc.make('Application', _Application, singleton=True, aliases=['App', 'app', 'application'])
