import uvicore
from uvicore.http.provider import Http
from uvicore.database.provider import Db
from uvicore.package import ServiceProvider
from uvicore.support.dumper import dump, dd  # type: ignore


@uvicore.provider()
class Auth(ServiceProvider, Db, Http):

    def register(self) -> None:
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
        # Define service provider registration control
        self.registers(self.package.config.registers)

        # Define Database Connections
        self.connections(
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
        self.models(['uvicore.auth.models'])

        # Define data seeders
        # NO - Auth shouldn't do its own seeding.  Let the app do it all.
        # You think?  What if a package is an app, then it runs seeders, but if that app is used
        # inside another package, you can't stop it from seeding.  Need to figure out overrideing seeders array better
        self.seeders(['uvicore.auth.database.seeders.seed'])

        # Define view and asset paths and configure the templating system
        self.define_views()

        # Define Web and API routes and prefixes
        self.define_routes()

    def define_views(self) -> None:
        """Define view and asset paths and configure the templating system"""

        # Define view paths
        #self.views(['uvicore.auth.http.views'])

        # Define public paths
        self.public(['uvicore.auth.http.public'])

        # Define asset paths
        self.assets(['uvicore.auth.http.public.assets'])

    def define_routes(self) -> None:
        """Define Web and API routes and prefixes"""

        # Define web routes
        # self.web_routes(
        #     module='uvicore.auth.http.routes.web.Web',
        #     prefix=self.package.config.web.prefix,
        #     #name_prefix=None,
        # )

        # Define api routes
        self.api_routes(
            module='uvicore.auth.http.routes.api.Api',
            prefix=self.package.config.api.prefix,
            #name_prefix='api',
        )
