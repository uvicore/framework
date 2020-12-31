import uvicore
from uvicore.package import ServiceProvider
from uvicore.support.dumper import dump, dd

@uvicore.provider()
class Console(ServiceProvider):

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
        pass


    def boot(self) -> None:
        # Register commands
        self.commands([
            # Register schematic generator commands
            {
                'group': {
                    'name': 'gen',
                    'parent': 'root',
                    'help': 'Schematic Generators',
                },
                'commands': [
                    {'name': 'command', 'module': 'uvicore.console.commands.generators.command'},
                ],
            }
        ])
