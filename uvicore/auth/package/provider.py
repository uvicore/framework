import uvicore
from uvicore.package import Provider
from uvicore.support.dumper import dump, dd
from uvicore.http.package.registers import Http
from uvicore.database.package.registers import Db


@uvicore.provider()
class Auth(Provider, Db, Http):

    def register(self) -> None:
        """Register package into the uvicore framework.
        All packages are registered before the framework boots.  This is where
        you define your packages configs, IoC bindings and early event listeners.
        Configs are deep merged only after all packages are registered.  No real
        work should be performed here as it is very early in the bootstraping
        process and we have no clear view of the full configuration system."""

        # Register IoC bindings
        # self.bind(
        #     name='Auth',
        #     object='uvicore.auth.auth._Auth',
        #     aliases=['auth']
        # )

        # Bind Tables
        #self.bind('uvicore.auth.database.tables.groups.Groups', 'uvicore.auth.database.tables.groups._Groups', singleton=True)
        #self.bind('uvicore.auth.database.tables.user_info.UserInfo', 'uvicore.auth.database.tables.user_info._UserInfo', singleton=True)
        #self.bind('uvicore.auth.database.tables.users.Users', 'uvicore.auth.database.tables.users._Users', singleton=True)

        # Bind Models
        #self.bind('uvicore.auth.models.group.Group', 'uvicore.auth.models.group.GroupModel')
        #self.bind('uvicore.auth.models.user.User', 'uvicore.auth.models.user.UserModel')
        #self.bind('uvicore.auth.models.user_info.UserInfo', 'uvicore.auth.models.user_info.UserInfoModel')

        # Register config
        self.configs([
            {'key': self.name, 'module': 'uvicore.auth.config.package.config'}
        ])

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

        # Define Database Connections
        self.register_db_connections(
            connections=self.package.config.database.connections,
            default=self.package.config.database.default
        )

        # Define all tables/models used by this package.
        # The goal is to load up all SQLAlchemy tables for complete metedata definitions.
        # If you separate tables vs models use self.tables(['myapp.database.tables.*])
        # If you use models only, or models with inline tables then use self.models(['myapp.models.*])
        # Optionally define your own models/__init__.py and import myapp.models to load every table.
        # Order does not matter as they are sorted topologically for ForeignKey dependencies
        # Using __init__.py now, so just import it
        #from uvicore.auth import models
        #dump(self.package)
        self.register_db_models(['uvicore.auth.models'])

        # Define data seeders
        # NO - Auth shouldn't do its own seeding.  Let the app do it all.
        # You think?  What if a package is an app, then it runs seeders, but if that app is used
        # inside another package, you can't stop it from seeding.  Need to figure out overrideing seeders array better
        self.register_db_seeders(['uvicore.auth.database.seeders.seed'])

        # Define view and asset paths and configure the templating system
        self.define_views()

        # Define Web and API routes and prefixes
        self.define_routes()

    def define_views(self) -> None:
        """Define view and asset paths and configure the templating system"""

        # Define view paths
        #self.views(['uvicore.auth.http.views'])

        # Define public paths
        self.register_http_public(['uvicore.auth.http.public'])

        # Define asset paths
        self.register_http_assets(['uvicore.auth.http.public.assets'])

    def define_routes(self) -> None:
        """Define Web and API routes and prefixes"""

        # Define web routes
        # self.register_http_web_routes(
        #     module='uvicore.auth.http.routes.web.Web',
        #     prefix=self.package.config.web.prefix,
        #     #name_prefix=None,
        # )

        # Define api routes
        self.register_http_api_routes(
            module='uvicore.auth.http.routes.api.Api',
            prefix=self.package.config.api.prefix,
            #name_prefix='api',
        )
