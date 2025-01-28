import uvicore
from uvicore.package import Provider
from uvicore.typing import Any, Dict
from uvicore.support.module import load
from uvicore.support.dumper import dump, dd
from uvicore.database.package import bootstrap
from uvicore.console.package.registers import Cli
from uvicore.foundation.events import app as AppEvents


@uvicore.provider()
class Database(Provider, Cli):

    def register(self) -> None:
        """Register package into the uvicore framework.
        All packages are registered before the framework boots.  This is where
        you define your packages configs, IoC bindings and early event listeners.
        Configs are deep merged only after all packages are registered.  No real
        work should be performed here as it is very early in the bootstraping
        process and we have no clear view of the full configuration system."""

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
        # We also connect on the fly in db.py def database()

        # FIXME, NO databases is obsolete, this does nothing
        @uvicore.events.handle(['uvicore.console.events.command.Startup', 'uvicore.console.events.command.PytestStartup', 'uvicore.http.events.server.Startup'])
        async def uvicore_startup(event):
            # Connect to all databases
            pass
            #await uvicore.db.connect(all_dbs=True)

        # Disconnect from all databases after the system has shutdown
        @uvicore.events.handle(['uvicore.console.events.command.Shutdown', 'uvicore.console.events.command.PytestShutdown', 'uvicore.http.events.server.Shutdown'])
        async def uvicore_shutdown(event):
            # Disconnect from all connected databases
            pass
            #await uvicore.db.disconnect(all_dbs=True)

    def boot(self) -> None:
        """Bootstrap package into the uvicore framework.
        Boot takes place after ALL packages are registered.  This means all package
        configs are deep merged to provide a complete and accurate view of all
        configuration. This is where you register, connections, models,
        views, assets, routes, commands...  If you need to perform work after ALL
        packages have booted, use the event system and listen to the booted event:
        self.events.listen('uvicore.foundation.events.app.Booted', self.booted)"""

        # Define service provider registration control
        self.registers(self.package.config.registers)

        # Define db commands
        self.register_cli_commands(
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
        self.register_cli_commands(
            group='gen',
            commands={
                'table': 'uvicore.database.commands.generators.table',
                'seeder': 'uvicore.database.commands.generators.seeder',
            }
        )
