import uvicore
from typing import Any
from uvicore.package import ServiceProvider
from uvicore.support.dumper import dump, dd
from uvicore.console.provider import Cli
from uvicore.support.module import load
from uvicore.console import group as cli_group
from uvicore.typing import Dict


@uvicore.provider()
class Console(ServiceProvider, Cli):

    def register(self) -> None:
        # Register IoC bindings
        #from uvicore.console.console import cli
        #dump('service------------')
        # self.bind('uvicore.console.console.cli', 'uvicore.console.console.cli',
        #     aliases=['Console', 'console', 'cli', 'cli2']
        # )

        # self.bind('Console', 'uvicore.console.console.cli',
        #     aliases=['uvicore.console.console.cli', 'console', 'cli', 'cli2']
        # )

        # After all providers are booted, fire up console with all groups and commands
        self.events.listen('uvicore.foundation.events.app.Booted', self.booted)

    def boot(self) -> None:

        # Define service provider registration control
        # No - Never allow this packages registrations to be disabled from other configs

        # Define commands
        self.commands(
            group='gen',
            help='Generate New Schematics (commands, models, views...)',
            commands={
                'command': 'uvicore.console.commands.generators.command'
            }
        )

    def booted(self, event: str, payload: Any) -> None:
        """Custom event handler for uvicore.foundation.events.app.Booted"""
        from uvicore.console.console import _cli as cli

        # Deep merge all command groups, this allows simple command extension!
        groups = Dict()
        for package in self.app.packages.values():
            if not 'console' in package: continue

            # Only register commands if package registration is allowed
            # AND if running from the console...OR if the command group is
            # 'http'.  We always want the http group regardless of cli or
            # http entrypoints.
            register = package.registers.commands
            is_console = uvicore.app.is_console
            for key, group in package.console['groups'].items():
                if (register and is_console) or key == 'http':
                    groups.merge({key: group})

        # Register each group and each groups commands
        click_groups = {}
        for key, group in groups.items():
            # Split key to find parent/child groups
            parts = key.split(':')
            parent = ':'.join(parts[0: -1])
            name = parts[-1]

            # Create a new click group if not exists
            @cli_group(help=group['help'])
            def click_group():
                pass
            click_groups[key] = click_group

            # Get click group based on key (this is how we handle sub groups)
            #click_group = click_groups[key]

            # Add all commands into this click_group
            for command_name, command_module in group.commands.items():
                # Dynamically import the commands module
                module = load(command_module).object
                click_group.add_command(module, command_name)

            # Add group to console
            if len(parts) == 1:
                # Root level group
                cli.add_command(click_group, name)
            else:
                # Sub group
                click_groups[parent].add_command(click_group, name)
