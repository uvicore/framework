import uvicore
from typing import Dict
from uvicore.package import ServiceProvider
from uvicore.support.dumper import dump, dd

@uvicore.provider()
class Database(ServiceProvider):

    def register(self) -> None:
        # Register IoC bindings
        # self.bind('Database', 'uvicore.database.db._Db',
        #     singleton=True,
        #     aliases=['database', 'db'],
        # )

        # Set uvicore.log global
        uvicore.db = uvicore.ioc.make('uvicore.database.db._Db')

        # Register event listeners
        # After all providers are registered (meaning configs merged)
        # Init the database system with all connection information
        self.events.listen('uvicore.foundation.events.app.Registered', self.registered)

    def registered(self, event: str, payload: Dict):
        default = uvicore.app.package(main=True).connection_default
        connections = []
        for package in uvicore.app.packages.values():
            for connection in package.connections:
                connections.append(connection)

        # Init the database with all connections
        uvicore.db.init(default, connections)

        # # Set default connection based on MAIN package
        # uvicore.db.default = uvicore.app.package(main=True).connection_default

        # # Add each packages connection
        # for package in uvicore.app.packages.values():
        #     for connection in package.connections:
        #         uvicore.db.add_connection(connection)

    def boot(self) -> None:
        # Define CLI commands to be added to the ./uvicore command line interface
        self.load_commands()

    def load_commands(self) -> None:
        """Define CLI commands to be added to the ./uvicore command line interface
        """
        # Register commands
        self.commands([
            # Register db commands
            {
                'group': {
                    'name': 'db',
                    'parent': 'root',
                    'help': 'Database Commands',
                },
                'commands': [
                    {'name': 'create', 'module': 'uvicore.database.commands.db.create'},
                    {'name': 'drop', 'module': 'uvicore.database.commands.db.drop'},
                    {'name': 'recreate', 'module': 'uvicore.database.commands.db.recreate'},
                    {'name': 'seed', 'module': 'uvicore.database.commands.db.seed'},
                    {'name': 'reseed', 'module': 'uvicore.database.commands.db.reseed'},
                    {'name': 'connections', 'module': 'uvicore.database.commands.db.connections'},
                ],
            },

            # Extend schematic generator commands
            {
                'group': {
                    'name': 'gen',
                    'parent': 'root',
                    'extend': True,
                },
                'commands': [
                    {'name': 'table', 'module': 'uvicore.database.commands.generators.table'},
                    {'name': 'seeder', 'module': 'uvicore.database.commands.generators.seeder'},
                ],
            }

        ])
