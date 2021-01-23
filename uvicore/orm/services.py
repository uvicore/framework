import uvicore
from typing import Dict
from uvicore.package import ServiceProvider
from uvicore.support.dumper import dump, dd
from uvicore.console.provider import Cli


@uvicore.provider()
class Orm(ServiceProvider, Cli):

    def register(self) -> None:
        pass
        # Register IoC bindings
        # Automatic - self.bind('Model', 'uvicore.orm.model._Model', aliases=['model'])
        # Automatic - self.bind('ModelMetaclass', 'uvicore.orm.metaclass._ModelMetaclass')

        #self.bind('Model', 'uvicore.orm.model._Model', aliases=['model'])
        #self.bind('ModelMetaclass', 'uvicore.orm.metaclass._ModelMetaclass')

    def boot(self) -> None:
        # Define service provider registration control
        self.registers(self.package.config.registers)

        # Define commands
        self.commands({
            # Extend schematic generator commands
            'gen': {
                'commands': {
                    'model': 'uvicore.orm.commands.generators.model',
                },
            }
        })
