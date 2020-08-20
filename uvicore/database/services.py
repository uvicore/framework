import uvicore
from typing import Dict
from uvicore.package import ServiceProvider
from uvicore.support.dumper import dump, dd


class Database(ServiceProvider):

    def register(self) -> None:
        """Register package into uvicore framework.
        All packages are registered before the framework boots.  This is where
        you define your packages configs and IoC bindings.  Configs are deep merged only after
        all packages are registered.  No real work should be performed here as it
        is very early in the bootstraping process and most internal processes are not
        instantiated yet.
        """
        # Register IoC bindings
        if self.app.is_async:
            #object = self.binding('DbAsync') or 'uvicore.database.async._Async'
            object = self.binding('DbSync') or 'uvicore.database.sync._Sync'
        else:
            object = self.binding('DbSync') or 'uvicore.database.sync._Sync'
        self.bind(
            name='Database',
            object=object,
            singleton=True,
            aliases=['database', 'db']
        )

        # Set uvicore.log global
        uvicore.db = uvicore.ioc.make('Database')

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
        """Bootstrap package into uvicore framework.
        Boot takes place after all packages are registered.  This means all package
        configs are deep merged to provide a complete and accurate view of all configs.
        This is where you load views, assets, routes, commands...
        """
        pass
