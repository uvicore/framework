import importlib
import sys
from typing import Any, Dict, List, Union

import uvicore
from collections import OrderedDict
#import typer_async as typer
from uvicore.contracts import Application, Package
from uvicore.contracts import Provider as ProviderInterface
from uvicore.contracts import Dispatcher
from uvicore.console import group as click_group
from uvicore.support.dumper import dd, dump
from uvicore.support.module import load, location
from uvicore.support.collection import Dic


@uvicore.service(aliases=['ServiceProvider', 'Provider'])
class ServiceProvider(ProviderInterface):

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
    def name(self) -> Dict:
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
        """bind here"""
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
            # Load module to get actual config value
            value = load(config['module']).object

            # Merge config value with complete config
            uvicore.config.merge(config['key'], value)

    def registers(self, options: Dict) -> None:
        if options is not None:
            self.package.registers = Dic(options)












    def viewsOLD(self, paths: List) -> None:
        # We DO allow these to be added if in CLI, through they are not actuall used
        # Why? So we can inspect them from ./uvicore package list

        # Dont load views if config is disabled
        if not self.package.registers.views: return

        for view in paths:
            # Find the actual file path of this view module
            view_path = location(view)

            # Add path to package
            self.package.view_paths.append(view_path)

    def assetsOLD(self, paths: List) -> None:
        # We DO allow these to be added if in CLI, through they are not actuall used
        # Why? So we can inspect them from ./uvicore package list

        # Dont load assets if config is disabled
        if not self.package.registers.assets: return

        for asset in paths:
            # Find the actual file path of this view module
            asset_path = location(asset)

            # Add path to package
            self.package.asset_paths.append(asset_path)

    def templateOLD(self, options: Dict) -> None:
        # We DO allow these to be added if in CLI, through they are not actuall used
        # Why? So we can inspect them from ./uvicore package list

        # Dont load templates if config is disabled
        if not self.package.registers.views: return

        # Add options to package
        self.package.template_options = options

    def web_routesOLD(self, routes_class: str) -> None:
        # Dont load routes if running in CLI
        if uvicore.app.is_console: return

        # Dont load routes if config is disabled
        if not self.package.registers.web_routes: return

        # Import and instantiate apps WebRoutes class
        from uvicore.http.routing.web_router import WebRouter
        WebRoutes = load(routes_class).object
        routes = WebRoutes(uvicore.app, self.package, WebRouter, self.package.web_route_prefix)
        routes.register()

    def api_routesOLD(self, routes_class: str) -> None:
        # Dont load routes if running in CLI
        if uvicore.app.is_console: return

        # Dont load routes if config is disabled
        if not self.package.registers.api_routes: return

        # Import and instantiate apps APIRoutes class
        from uvicore.http.routing.api_router import ApiRouter
        ApiRoutes = load(routes_class).object
        routes = ApiRoutes(uvicore.app, self.package, ApiRouter, self.package.api_route_prefix)
        routes.register()





    def middleware(self, middleware: OrderedDict):
        # Dont load routes if running in CLI
        if uvicore.app.is_console: return

        # Dont load middleware if config is disabled
        if not self.package.registers.middleware: return

        dump('hi middleware')
        dump(middleware)
        dump(self.app.http)





    def modelsOLD(self, models: List[str]) -> None:
        # Dont load models if config is disabled
        if not self.package.registers.models: return

        # Import all defined models so SQLAlchemy metedata is built
        for model in models:
            #if model not in self.package.models:
                #self.package.models.append(model)
            load(model)

    def tablesOLD(self, tables: List[str]) -> None:
        # Dont load tables if config is disabled
        if not self.package.registers.tables: return

        # Import all defined tables so SQLAlchemy metedata is built
        for table in tables:
            #if table not in self.package.tables:
                #self.package.tables.append(model)
            load(model)

    def seedersOLD(self, seeders: List[str]) -> None:
        for seeder in seeders:
            if seeder not in self.package.seeders:
                self.package.seeders.append(seeder)

    def commandsOLD(self, options: Dict) -> None:
        # Only register command if running from the console
        # or from the http:serve command (register only the http group).
        # Do NOT register apps commands if apps config.register_commands if False
        register = self.package.registers.commands
        if uvicore.app.is_http: register = False
        for group in options:
            if group.get('group').get('name') == 'http':
                for command in group.get('commands'):
                    if command.get('name') == 'serve':
                        register = True
                        break;
        if not register: return

        # Main Click Group from Ioc
        #cli = uvicore.ioc.make('uvicore.console.console._cli')
        #cli = uvicore.ioc.make('Console')
        from uvicore.console.console import _cli as cli

        # Register each group and each groups commands
        click_groups = {}
        for group in options:
            group_name = group.get('group').get('name')
            group_parent = group.get('group').get('parent')
            group_help = group.get('group').get('help')
            extend = group.get('group').get('extend') or False
            commands = group.get('commands') or []

            if extend and group_name in self.__class__.__click_groups__:
                # Group already registered in a previous package, extend it
                group = self.__class__.__click_groups__[group_name]
            else:
                # Create a new click group
                @click_group(help=group_help)
                def group():
                    pass
                self.__class__.__click_groups__[group_name] = group

            # Track this one packages multiple groups
            click_groups[group_name] = group

            # Add each command to this new click group
            for command in commands:
                click_command = load(command.get('module')).object

                if 'Typer' in str(click_command):
                    # Typer
                    import typer
                    group.add_command(typer.main.get_command(click_command), command.get('name'))
                else:
                    # Click
                    group.add_command(click_command, command.get('name'))

            if group_parent == 'root':
                # Add this click group to main root click group
                #uvicore.app.cli.add_command(group, group_name)
                cli.add_command(group, group_name)
            else:
                # Add this click group to another parent group
                click_groups[group_parent].add_command(group, group_name)



# IoC Class Instance
#_ServiceProviderIoc: _ServiceProvider = uvicore.ioc.make('ServiceProvider', _ServiceProvider, aliases=['service', 'provider'])

#class ServiceProvider(_ServiceProviderIoc, ProviderInterface):
#    pass

# Public API for import * and doc gens
#__all__ = ['ServiceProvider', '_ServiceProvider']
