import sys
import importlib
from typing import Dict, List, Any

import uvicore
from uvicore.support.click import click, group_kargs, typer
from uvicore.support.module import load, location
from uvicore.foundation import Package
from uvicore.support.dumper import dump, dd
from uvicore.contracts import Provider as ProviderInterface


class ServiceProvider(ProviderInterface):

    def bind(self,
        name: str,
        object: Any,
        *,
        factory: Any = None,
        kwargs: Dict = None,
        singleton: bool = False,
        aliases: List = []
    ) -> None:
        uvicore.ioc.bind(name, object, factory=factory, kwargs=kwargs, singleton=singleton, aliases=aliases)


    def views(self, package: Package, paths: List) -> None:
        # We DO allow these to be added if in CLI, through they are not actuall used
        # Why? So we can inspect them from ./uvicore package list

        # Dont load views if config is disabled
        if not package.register_views: return

        for view in paths:
            # Find the actual file path of this view module
            view_path = location(view)

            # Add path to package
            package.view_paths.append(view_path)

    def assets(self, package: Package, paths: List) -> None:
        # We DO allow these to be added if in CLI, through they are not actuall used
        # Why? So we can inspect them from ./uvicore package list

        # Dont load assets if config is disabled
        if not package.register_assets: return

        for asset in paths:
            # Find the actual file path of this view module
            asset_path = location(asset)

            # Add path to package
            package.asset_paths.append(asset_path)


    def template(self, package: Package, options: Dict) -> None:
        # We DO allow these to be added if in CLI, through they are not actuall used
        # Why? So we can inspect them from ./uvicore package list

        # Dont load templates if config is disabled
        #if not package.register_views: return

        # Add options to package
        package.template_options = options

    def web_routes(self, package: Package, routes_class: Any) -> None:
        # Dont load routes if running in CLI
        if uvicore.app.is_console: return

        # Dont load routes if config is disabled
        if not package.register_web_routes: return

        # Import and instantiate apps WebRoutes class
        from uvicore.http.routing import WebRouter
        WebRoutes = load(routes_class).object
        WebRoutes(uvicore.app, package, WebRouter, package.web_route_prefix)

    def api_routes(self, package: Package, routes_class: Any) -> None:
        # Dont load routes if running in CLI
        if uvicore.app.is_console: return

        # Dont load routes if config is disabled
        if not package.register_api_routes: return

        # Import and instantiate apps APIRoutes class
        from uvicore.http import APIRouter
        APIRoutes = load(routes_class).object
        APIRoutes(uvicore.app, package, APIRouter, package.api_route_prefix)

    def commands(self, package: Package, options: Dict) -> None:
        # Only register command if running from the console
        # or from the http:serve command (register only the http group).
        # Do NOT register apps commands if apps config.register_commands if False
        register = package.register_commands
        if uvicore.app.is_http: register = False
        for group in options:
            if group.get('group').get('name') == 'http':
                for command in group.get('commands'):
                    if command.get('name') == 'serve':
                        register = True
                        break;
        if not register: return

        # Register each group and each groups commands
        click_groups = {}
        for group in options:
            group_name = group.get('group').get('name')
            group_parent = group.get('group').get('parent')
            group_help = group.get('group').get('help')
            commands = group.get('commands')

            # Create a new click group
            @click.group(**group_kargs, help=group_help)
            def group():
                pass
            click_groups[group_name] = group

            # Add each command to this new click group
            for command in commands:
                click_command = load(command.get('module')).object
                group.add_command(typer.main.get_command(click_command), command.get('name'))

            if group_parent == 'root':
                # Add this click group to root
                uvicore.app.cli.add_command(group, group_name)
            else:
                # Add this click group to another parent group
                click_groups[group_parent].add_command(group, group_name)

    def command_OLD(self, *, name: str, help: str = None, commands: List, force: bool = False) -> None:
        # Don't load commands if not running in CLI
        if not force and not uvicore.app.is_console: return

        # Defining the name as 'root' makes the commands a root level command
        # NOT a click subcommand nested under a name

        if name != 'root':
            # Create a new click group for all commands in this app
            @click.group(**group_kargs, help=help)
            def group():
                pass

        # Add each apps commands to their own group
        for command_name, module in commands:
            click_command = load(module).object
            if name == 'root':
                # Add all uvicore commands to main command (NOT an app based subcommand)
                uvicore.app.cli.add_command(typer.main.get_command(click_command), command_name)
            else:
                # Add all apps commands to a click subcommand
                group.add_command(typer.main.get_command(click_command), command_name)

        if name != 'root':
                uvicore.app.cli.add_command(group, name)

    def configs(self, options: List[Dict]) -> None:
        for config in options:
            # Load module to get actual config value
            value = load(config['module']).object

            # Merge config value with complete config
            uvicore.config.merge(config['key'], value)
