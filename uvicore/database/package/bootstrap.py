import uvicore
from uvicore.typing import Dict
from uvicore.events import Handler
from uvicore.support.module import load
from uvicore.support.dumper import dump, dd
from uvicore.foundation.events.app import Booted as OnAppBooted


class Database(Handler):

    def __call__(self, event: OnAppBooted):
        """Bootstrap the Database after the Application is Booted"""

        # Gather all connections, models, tables
        # No need to gather seeder classes, I get those in the ./uvicore db seed command
        connections = Dict()
        models = []; tables = []
        last_default = None; app_default = None
        for package in uvicore.app.packages.values():
            if not 'database' in package: continue

            # Get last defined default connection
            if package.database.connection_default: last_default = package.database.connection_default

            # Get running app default connection
            if package.main and package.database.connection_default: app_default = package.database.connection_default

            # Append connections
            connections.merge(package.database.connections)

            # Append models
            models.extend(package.database.models or [])

            # Append tables
            tables.extend(package.database.tables or [])

        # Initialize Database with all connections at once
        uvicore.db.init(app_default or last_default, connections)

        # Add all final merged connections to running_config
        uvicore.app.add_running_config('database.connections', uvicore.db.connections)

        # Dynamically Import models, tables and seeders
        for model in models: load(model)
        for table in tables: load(table)

        # Pydantic v2 builds a model's ENTIRE related-schema graph eagerly the moment
        # the model is "rebuilt" (forward refs resolved).  ORM models reference their
        # relations via forward references and import those related models at the BOTTOM
        # of each module to break circular imports, so a per-module model_rebuild() can
        # fire before the whole graph is importable.  Now that every model module above
        # is fully imported, do a single authoritative rebuild pass: each model's forward
        # refs (relations) now resolve against fully-populated module namespaces.
        for name in uvicore.ioc.binding(type='model').keys():
            entity = uvicore.ioc.make(name)
            model_rebuild = getattr(entity, 'model_rebuild', None)
            if model_rebuild:
                model_rebuild(force=True)
