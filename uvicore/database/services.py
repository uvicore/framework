import uvicore
from uvicore.typing import Any, Dict
from uvicore.package import ServiceProvider
from uvicore.support.dumper import dump, dd
from uvicore.support.module import load
from uvicore.console.provider import Cli
from uvicore.database import bootstrap
from uvicore.foundation.events import app as AppEvents


@uvicore.provider()
class Database(ServiceProvider, Cli):

    def register(self) -> None:
        # Register IoC bindings
        # self.bind('Database', 'uvicore.database.db._Db',
        #     singleton=True,
        #     aliases=['database', 'db'],
        # )

        # Set uvicore.log global
        uvicore.db = uvicore.ioc.make('uvicore.database.db.Db')

        # Register event listeners
        AppEvents.Booted.listen(bootstrap.Database)

        # Event Handlers
        # String based events instead of class based because HTTP may not even
        # be installed, so importing the HTTP event would cause an issue.

        # Connect to all databases one time, after the system has started up
        @uvicore.events.handle(['uvicore.console.events.command.Startup', 'uvicore.http.events.server.Startup'])
        async def uvicore_startup(event):
            # Loop each database and connect()
            # I used to do it on-the-fly in db.py but was getting pool errors
            for metakey, database in uvicore.db.databases.items():
                #dump('Connecting to ' + metakey)
                await database.connect()

        # Disconnect from all databases after the system has shutdown
        @uvicore.events.handle(['uvicore.console.events.command.Shutdown', 'uvicore.http.events.server.Shutdown'])
        async def uvicore_shutdown(event):
            # Disconnect from all connected databases
            await uvicore.db.disconnect(from_all=True)

    def boot(self) -> None:
        # Define service provider registration control
        self.registers(self.package.config.registers)

        # Define db commands
        self.commands(
            group='db',
            help='Database Commands',
            commands={
                'create': 'uvicore.database.commands.db.create',
                'drop': 'uvicore.database.commands.db.drop',
                'recreate': 'uvicore.database.commands.db.recreate',
                'seed': 'uvicore.database.commands.db.seed',
                'reseed': 'uvicore.database.commands.db.reseed',
                'connections': 'uvicore.database.commands.db.connections',
            }
        )

        # Extend schematic generator commands
        self.commands(
            group='gen',
            commands={
                'table': 'uvicore.database.commands.generators.table',
                'seeder': 'uvicore.database.commands.generators.seeder',
            }
        )
