import uvicore
from uvicore.typing import Dict
from uvicore.events import Handler
from uvicore.support.dumper import dump, dd
from uvicore.foundation.events.app import Booted as OnAppBooted


class Redis(Handler):

    def __call__(self, event: OnAppBooted):
        """Bootstrap Redis after the Application is Booted"""

        connections = Dict()
        last_default = None; app_default = None
        for package in uvicore.app.packages.values():
            if not 'redis' in package: continue

            # Get last defined default connection
            if package.redis.connection_default: last_default = package.redis.connection_default

            # Get running app default connection
            if package.main and package.redis.connection_default: app_default = package.redis.connection_default

            # Append connections
            connections.merge(package.redis.connections)

        # Add all final merged connections to running_config
        uvicore.app.add_running_config('redis.connections', connections)

        # Initialize Redis with all connections at once
        redis = uvicore.ioc.make('uvicore.redis.redis.Redis')
        redis.init(app_default or last_default, connections)
