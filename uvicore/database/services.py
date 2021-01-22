import uvicore
from uvicore.typing import Any
from uvicore.package import ServiceProvider
from uvicore.support.dumper import dump, dd
from uvicore.support.module import load
from uvicore.console.provider import Cli


@uvicore.provider()
class Database(ServiceProvider, Cli):

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
        #self.events.listen('uvicore.foundation.events.app.Registered', self.registered)

        # After all providers are booted, fire up database with all package
        # connections, modules, tables, seeders...
        self.events.listen('uvicore.foundation.events.app.Booted', self.booted)

    def boot(self) -> None:
        # Define commands
        self.commands({
            # Register db commands
            'db': {
                'help': 'Database Commands',
                'commands': {
                    'create': 'uvicore.database.commands.db.create',
                    'drop': 'uvicore.database.commands.db.drop',
                    'recreate': 'uvicore.database.commands.db.recreate',
                    'seed': 'uvicore.database.commands.db.seed',
                    'reseed': 'uvicore.database.commands.db.reseed',
                    'connections': 'uvicore.database.commands.db.connections',
                }
            },

            # Extend schematic generator commands
            'gen': {
                'commands': {
                    'table': 'uvicore.database.commands.generators.table',
                    'seeder': 'uvicore.database.commands.generators.seeder',
                }
            }
        })

    def registered_OBSOLETE(self, event: str, payload: Any):
        """Custom event handler for uvicore.foundation.events.app.Registered"""
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

    def booted(self, event: str, payload: Any) -> None:
        """Custom event handler for uvicore.foundation.events.app.Booted"""

        # Gather all connections, models, tables and seeders
        connections = []; models = []; tables = []; seeders = []
        last_default = None; app_default = None
        for package in self.app.packages.values():
            if not 'database' in package: continue

            # Get last defined default connection
            if package.database.connection_default: last_default = package.database.connection_default

            # Get running app default connection
            if package.main and package.database.connection_default: app_default = package.database.connection_default

            # Append connections
            connections.extend(package.database.connections or [])

            # Append models
            models.extend(package.database.models or [])

            # Append tables
            tables.extend(package.database.tables or [])

            # Append seeders
            seeders.extend(package.database.seeders or [])

        # Initialize Database with all connections at once
        uvicore.db.init(app_default or last_default, connections)

        # Dynamically Import models, tables and seeders
        for model in models: load(model)
        for table in tables: load(table)
        for seeder in seeders: load(seeder)
        #dump(connections, models, tables, seeders, last_default, app_default)
