import uvicore
from uvicore.typing import Dict
from uvicore.package import Provider
from uvicore.support.dumper import dump, dd
from uvicore.console.package.registers import Cli
from uvicore.support.module import load
from uvicore.console import group as cli_group
from uvicore.console.package import bootstrap
from uvicore.foundation.events import app as AppEvents


@uvicore.provider()
class Console(Provider, Cli):

    def register(self) -> None:
        """Register package into the uvicore framework.
        All packages are registered before the framework boots.  This is where
        you define your packages configs, IoC bindings and early event listeners.
        Configs are deep merged only after all packages are registered.  No real
        work should be performed here as it is very early in the bootstraping
        process and we have no clear view of the full configuration system."""

        # Register IoC bindings
        #from uvicore.console.console import cli
        #dump('service------------')
        # self.bind('uvicore.console.console.cli', 'uvicore.console.console.cli',
        #     aliases=['Console', 'console', 'cli', 'cli2']
        # )

        # self.bind('Console', 'uvicore.console.console.cli',
        #     aliases=['uvicore.console.console.cli', 'console', 'cli', 'cli2']
        # )

        # Register event listeners
        # Priority is 90 because we want the console to be bootstrapped after most
        # other uvicore services like Database.  If database is not initialized, and you import
        # a DB model/table from a command, it will error because the connection strings have not yet
        # been initialized.
        AppEvents.Booted.listen(bootstrap.Console, priority=90)
        #uvicore.events.listen('uvicore.foundation.events.app.Booted', bootstrap.Console, priority=90)
        #uvicore.events.listen('uvicore.foundation.events.app.*', bootstrap.Console, priority=90)

    def boot(self) -> None:
        """Bootstrap package into the uvicore framework.
        Boot takes place after ALL packages are registered.  This means all package
        configs are deep merged to provide a complete and accurate view of all
        configuration. This is where you register, connections, models,
        views, assets, routes, commands...  If you need to perform work after ALL
        packages have booted, use the event system and listen to the booted event:
        self.events.listen('uvicore.foundation.events.app.Booted', self.booted)"""

        # Define service provider registration control
        # No - Never allow this packages registrations to be disabled from other configs

        # Define commands
        self.register_cli_commands(
            group='gen',
            help='Generate New Schematics (commands, models, views...)',
            commands={
                'command': 'uvicore.console.commands.generators.command'
            }
        )
