import os
import sys
from collections import OrderedDict as ODict
from typing import Dict, List, NamedTuple, OrderedDict, Tuple, Any

import uvicore
from uvicore import config
from uvicore.configuration import Config
from uvicore.contracts import Application as ApplicationInterface
from uvicore.contracts import Server as ServerInterface
from uvicore.contracts import Config as ConfigInterface
from uvicore.contracts import Package as PackageInterface
from uvicore.contracts import Template as TemplateInterface
from uvicore.support.dumper import dd, dump
from uvicore.support.module import load, location
from uvicore.http import templates

from ..database.connection import Connection
from .cli import cli as ClickGroup


class _Application(ApplicationInterface):
    """Main uvicore application class.  Import Application IoC to instantiate."""

    # Class Variables (state independent of instantiation)
    #booted: bool = False

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
    def cli(self) -> Any:
        return self._cli

    @property
    def db(self) -> Any:
        return self._db

    @property
    def config(self) -> ConfigInterface:
        return self._config

    @property
    def providers(self) -> List[Tuple]:
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
    def packages(self) -> List[PackageInterface]:
        return self._packages

    @property
    def path(self) -> str:
        return self._path

    @property
    def name(self) -> str:
        return self._name

    @property
    def vendor(self) -> str:
        return self._vendor

    @property
    def module(self) -> str:
        return self._module


    #version: str = uvicore.__version__
    # """Uvicore framework version number"""

    # debug: bool = False
    # """Debug mode for entire application"""

    # perfs: List = []
    # """List of all perf dumps for performance tuning"""

    # http: ServerInterface = None
    # """HTTP Server Instance"""

    # template: TemplateInterface = None
    # """HTML Templating System"""

    # cli: Any = None
    # """Main click command group"""

    # config: ConfigInterface = None
    # """Configuration system"""

    # providers: List[Tuple] = []
    # """List of providers defined in all packages"""

    # registered: bool = False
    # """All providers have been registered"""

    # booted: bool = False
    # """All providers have been booted"""

    # is_console: bool = False
    # """App running from CLI (not serving web or API)"""

    # is_http: bool = False
    # """App running as HTTP server (not as CLI)"""

    # is_async: bool = False
    # """App running in async mode (HTTP).  CLI is not async"""

    # packages: List[PackageInterface] = []
    # """List of all packages defined from providers"""

    # path: str = None
    # """Base path of running application"""

    # name: str = None
    # """Short name of running application"""

    # vendor: str = None
    # """Vendor of running application"""

    # module: str = None
    # """Full module path of running application"""

    def __init__(self):
        # Instance variables
        self._version = uvicore.__version__
        self._debug = False
        self._perfs = []
        self._http = None
        self._template = None
        self._cli = None
        self._db = None
        self._config = None
        self._providers = []
        self._registered = False
        self._booted = False
        self._is_console = False
        self._is_http = False
        self._is_async = False
        self._packages = []
        self._path = None
        self._name = None
        self._vendor = None
        self._module = None

        # Instantiate uvicore singletons
        uvicore.config = Config()

        # Pass through attributes
        self._config = uvicore.config

    def bootstrap(self, app_config: Dict, path: str, is_console: bool) -> None:
        # Silently do not bootstrap multiple times
        if self.booted: return

        # App name and base_path
        self._path = path
        self._name = app_config.get('name')
        self._vendor = app_config.get('vendor')
        self._module = app_config.get('module')

        # Detect if running in console (to register commands)
        # Ensure console is False even when running ./uvicore http serve
        self._is_console = is_console
        if "'http', 'serve'" in str(sys.argv):
            self._is_console = False
        self._is_http = not self.is_console

        # Always set the cli instance, though commands won't be added if not is_console
        self._cli = ClickGroup

        # Add main app config
        self._config.set('app', app_config)

        # Detect debug flag from main app config
        self._debug = app_config['debug']

        # Perf
        self.perf('|-foundation.application.bootstrap()')
        self.perf('|--is_console: ' + str(self.is_console))

        # Build recursive providers graph
        self._build_provider_graph(self.module)

        # Register all providers
        self._register_providers()

        # Merge Providers (merges configs and creates actual Package class)
        self._merge_providers()

        # Create HTTP Server instance
        self._create_http_server()

        # Create Database instance
        self._create_database_instance()

        # Boot all providers
        self._boot_providers()

        # Mount static asset route
        self._mount_static_assets()

        # Create templating Environment
        self._create_template_environment()

        # Return application
        return self

    def _create_http_server(self) -> None:
        if self.is_http:
            self.perf('|--firing up HTTP server')
            from uvicore.http import Server
            self._http = Server(
                debug=self.config('app.debug'),
                title=self.config('app.openapi.title'),
                version=self.version,
                openapi_url=self.config('app.openapi.url'),
                docs_url=self.config('app.openapi.docs_url'),
                redoc_url=self.config('app.openapi.redoc_url'),
            )
            self._is_async = True

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

    def _mount_static_assets(self) -> None:
        # Mount static asset directories
        # Must be after _boot_providers() since packages register view info there
        if self.is_console: return

        from uvicore.http.static import StaticFiles

        # Get all packages asset paths
        paths = []
        for package in self.packages:
            for path in package.asset_paths:
                if path not in paths:
                    paths.append(path)

        # Mount all directories to /assets
        # Last directory defined WINS, which fits our last provider wins
        self.http.mount('/static', StaticFiles(directories=paths), name='static')

    def _create_template_environment(self) -> None:
        # Instantiate template environment with all paths, filters, tests...
        # Must be after _boot_providers() since packages register view info there
        if self.is_console: return

        # Instantiate template
        self._template = templates.Jinja()

        # Add all package view paths to template environment
        for package in self.packages:
            for path in package.view_paths:
                self.template.include_path(path)

        # Add all package template options to template environment
        options = package.template_options
        if 'context_functions' in options:
            for f in options['context_functions']:
                self.template.include_context_function(**f)
        if 'context_filters' in options:
            for f in options['context_filters']:
                self.template.include_context_filter(**f)
        if 'filters' in options:
            for f in options['filters']:
                self.template.include_filter(**f)
        if 'tests' in options:
            for f in options['tests']:
                self.template.include_test(**f)

        # Create new template environment
        self.template.init()

    def _register_providers(self) -> None:
        self.perf('|--registering providers')
        for (app, module) in self.providers:
            path = app + '.' + module
            self.perf('|---' + path)

            # Instantiate the provider and call boot()
            provider = load(path).mod()
            provider.register(self)
        self._registered = True

    def _merge_providers(self) -> None:
        self.perf('|--merging providers')
        for (app, module) in self.providers:
            path = app + '.' + module
            self.perf('|---' + path)

            # Load this packages config/app.py and merge into package config
            app_config = load(app + '.config.app.app').mod
            config_prefix = app_config.get('config_prefix')
            app_name = app_config.get('name')
            self.config.set(config_prefix + '.app', app_config)

            # Load this packages main config
            package_config = self.config(config_prefix)

            # Main app
            main = True if app_name == self.name else False

            # Route prefix
            web_route_prefix = None
            api_route_prefix = None
            if 'route' in package_config:
                web_route_prefix = package_config.get('route').get('web_prefix')
                api_route_prefix = package_config.get('route').get('api_prefix')

            # Database connections
            connections = []
            if 'database' in package_config:
                for name, connection in package_config.get('database').get('connections').items():
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
                        default=True if name == package_config.get('database').get('default') else False,
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
            package = uvicore.Package(
                name=app_config.get('name'),
                vendor=app_config.get('vendor'),
                module=app_config.get('module'),
                location=location(app_config.get('module')),
                main=main,
                config_prefix=app_config.get('config_prefix'),
                web_route_prefix=web_route_prefix,
                api_route_prefix=api_route_prefix,
                view_paths=[],
                asset_paths=[],
                template_options={},
                register_web_routes=True if package_config.get('register_web_routes') else False,
                register_api_routes=True if package_config.get('register_api_routes') else False,
                register_views=True if package_config.get('register_views') else False,
                register_assets=True if package_config.get('register_assets') else False,
                register_commands=True if package_config.get('register_commands') else False,
                connections=connections,
            )
            self._packages.append(package)

    def _boot_providers(self) -> None:
        self.perf('|--booting providers')
        for (app, module) in self.providers:
            path = app + '.' + module
            self.perf('|---' + path)

            # Get this providers package
            package = self.package(module=app)

            # Import the provider and call boot()
            provider = load(path).mod()
            provider.boot(self, package)
        #__class__.booted = True
        self._booted = True
        self.perf('--' + str(self.providers))

    def _build_provider_graph_DICT(self, module: str, package: str = None) -> None:
        if package:
            self._providers[module] = package
        app_config = load(module + '.config.app.app').mod
        packages = app_config['packages']
        for package in packages:
            if package.get('module') not in self.providers:
                return self._build_provider_graph(package.get('module'), package)
        return providers

    def _build_provider_graph(self, app: str, module: str = None) -> None:
        if module:
            self._providers.append((app, module))
        app_config = load(app + '.config.app.app').mod
        providers = app_config['providers']
        for (app, module) in providers:
            #app, module = provider
            #path = app + '.' + module
            if (app, module) not in self.providers:
                self._build_provider_graph(app, module)

    def package(self, name: str = None, module: str = None, main: bool = False) -> PackageInterface:
        if name:
            return next(package for package in self.packages if package.name == name)
        elif module:
            return next(package for package in self.packages if package.module == module)
        elif main:
            return next(package for package in self.packages if package.main == True)

    def perf(self, item) -> None:
        if self.debug:
            self.perfs.append(item)
            print(item)

    def dump(self, *args) -> None:
        dump(*args)

    def dd(self, *args) -> None:
        dd(*args)


# IoC Application class
Application = uvicore.ioc.make('Application')

# Public API for import * and doc gens
__all__ = ['Application']
