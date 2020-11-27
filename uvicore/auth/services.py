import uvicore
from uvicore.package import ServiceProvider
from uvicore.support.dumper import dump, dd


@uvicore.provider()
class Auth(ServiceProvider):

    def register(self) -> None:
        """Register package into uvicore framework.
        All packages are registered before the framework boots.  This is where
        you define your packages configs and IoC bindings.  Configs are deep merged only after
        all packages are registered.  No real work should be performed here as it
        is very early in the bootstraping process and most internal processes are not
        instantiated yet."""

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
            {'key': self.name, 'module': 'uvicore.auth.config.auth.config'}
        ])

    def boot(self) -> None:
        """Bootstrap package into uvicore framework.
        Boot takes place after all packages are registered.  This means all package
        configs are deep merged to provide a complete and accurate view of all configs.
        This is where you load views, assets, routes, commands..."""

        # Define CLI commands to be added to the ./uvicore command line interface
        #self.load_commands()

        # Define all tables/models used by this package.
        # The goal is to load up all SQLAlchemy tables for complete metedata definitions.
        # If you separate tables vs models use self.tables(['myapp.database.tables.*])
        # If you use models only, or models with inline tables then use self.models(['myapp.models.*])
        # Optionally define your own models/__init__.py and import myapp.models to load every table.
        # Order does not matter as they are sorted topologically for ForeignKey dependencies

        # Using __init__.py now, so just import it
        from uvicore.auth import models
        #self.models([
        #   'uvicore.auth.models.*',
        #])

        # Define data seeders
        # NO - Auth shouldn't do its own seeding.  Let the app do it all.
        # You think?  What if a package is an app, then it runs seeders, but if that app is used
        # inside another package, you can't stop it from seeding.  Need to figure out overrideing seeders array better
        # self.seeders([
        #     'uvicore.auth.database.seeders.seeders.seed'
        # ])

    def load_commands(self) -> None:
        """Define CLI commands to be added to the ./uvicore command line interface"""

        group = 'auth'
        self.commands([
            {
                'group': {
                    'name': group,
                    'parent': 'root',
                    'help': 'Auth Commands',
                },
                #'commands': []
                   #{'name': 'test', 'module': 'mreschke.wiki.commands.test.cli'},
                #],
            },
            {
                'group': {
                    'name': 'db',
                    'parent': group,
                    'help': 'Auth DB Commands',
                },
                'commands': [
                    {'name': 'create', 'module': 'uvicore.auth.commands.db.create'},
                    {'name': 'drop', 'module': 'uvicore.auth.commands.db.drop'},
                    {'name': 'recreate', 'module': 'uvicore.auth.commands.db.recreate'},
                    {'name': 'seed', 'module': 'uvicore.auth.commands.db.seed'},
                ],
            }
        ])

