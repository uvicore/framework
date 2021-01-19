import uvicore
from typing import Dict
from uvicore.package import ServiceProvider
from uvicore.support.dumper import dump, dd

@uvicore.provider()
class Orm(ServiceProvider):

    def register(self) -> None:
        pass
        # Register IoC bindings
        # Automatic - self.bind('Model', 'uvicore.orm.model._Model', aliases=['model'])
        # Automatic - self.bind('ModelMetaclass', 'uvicore.orm.metaclass._ModelMetaclass')

        #self.bind('Model', 'uvicore.orm.model._Model', aliases=['model'])
        #self.bind('ModelMetaclass', 'uvicore.orm.metaclass._ModelMetaclass')

    def boot(self) -> None:
        # Define CLI commands to be added to the ./uvicore command line interface
        self.load_commands()

    def load_commands(self) -> None:
        # Register commands
        self.commands([
            # Extend schematic generator commands
            {
                'group': {
                    'name': 'gen',
                    'parent': 'root',
                    'extend': True,
                },
                'commands': [
                    {'name': 'model', 'module': 'uvicore.orm.commands.generators.model'},
                ],
            }
        ])

