import uvicore
from uvicore.typing import Dict
from uvicore.package import ServiceProvider
from uvicore.support.dumper import dump, dd
from uvicore.console.provider import Cli
from uvicore.support.module import load
from uvicore.console import group as cli_group
from uvicore.console import bootstrap
from uvicore.foundation.events import app as AppEvents


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

        # Register event listeners
        AppEvents.Booted.listen(bootstrap.Console)

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
