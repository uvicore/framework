import uvicore
from uvicore.typing import Dict
from uvicore.events import Handler
from uvicore.support.module import load
from uvicore.support.dumper import dump, dd
from uvicore.console import group as cli_group
from uvicore.foundation.events.app import Booted as OnAppBooted


class Console(Handler):

    def __call__(self, event: OnAppBooted):
        """Bootstrap the Console after the Application is Booted"""

        #from uvicore.console.console import cli
        cli = uvicore.ioc.make('uvicore.console.console.cli')

        # Deep merge all command groups, this allows simple command extension!
        groups = Dict()
        for package in uvicore.app.packages.values():
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
