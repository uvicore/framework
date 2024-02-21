import uvicore
from uvicore.package import Provider
from uvicore.support.dumper import dump, dd
from uvicore.http.package.registers import Http
from uvicore.database.package.registers import Db
from uvicore.console.package.registers import Cli
from uvicore.redis.package.registers import Redis


@uvicore.provider()
class App1(Provider, Cli, Db, Redis, Http):

    def register(self) -> None:
        """Register package into the uvicore framework.
        All packages are registered before the framework boots.  This is where
        you define your packages configs, IoC bindings and early event listeners.
        Configs are deep merged only after all packages are registered.  No real
        work should be performed here as it is very early in the bootstraping
        process and we have no clear view of the full configuration system."""

        # Register configs
        # If config key already exists items will be deep merged allowing
        # you to override granular aspects of other package configs
        self.configs([
            {'key': self.name, 'value': self.package_config},
            {'key': 'uvicore.auth', 'module': 'app1.config.auth.auth'},
        ])

        # Bind Tables
        #self.bind('app1.database.tables.comments.Comments', 'app1.database.tables.comments._Comments', singleton=True)
        #self.bind('app1.database.tables.contacts.Contacts', 'app1.database.tables.contacts._Contacts', singleton=True)
        #self.bind('app1.database.tables.post_tags.PostTags', 'app1.database.tables.post_tags._PostTags', singleton=True)
        #self.bind('app1.database.tables.posts.Posts', 'app1.database.tables.posts._Posts', singleton=True)
        #self.bind('app1.database.tables.tags.Tags', 'app1.database.tables.tags._Tags', singleton=True)

        # Bind Models
        #self.bind('app1.models.contact.Contact', 'app1.models.contact.ContactModel')
        #self.bind('app1.models.comment.Comment', 'app1.models.comment.CommentModel')
        #self.bind('app1.models.tag.Tag', 'app1.models.tag.TagModel')
        #self.bind('app1.models.post.Post', 'app1.models.post.PostModel')


        # These do not work as they are too high up in the bootstrap process.  They have already been loaded
        # before this provider even hits.  Use app.config bindings array instead
        #self.bind_override('uvicore.foundation.application.Application', 'app1.overrides.application.Application')
        #self.bind_override('uvicore.package.Package', 'app1.overrides.package.Package')


        # Test bind overrides instead of app.config bindings array - works, but I have in app.config for now
        #self.bind_override('uvicore.auth.database.tables.users.Users', 'app1.database.tables.users.Users')
        #self.bind_override('uvicore.auth.models.user.User', 'app1.models.user.User')

    def boot(self) -> None:
        """Bootstrap package into the uvicore framework.
        Boot takes place after ALL packages are registered.  This means all package
        configs are deep merged to provide a complete and accurate view of all
        configuration. This is where you register, connections, models,
        views, assets, routes, commands...  If you need to perform work after ALL
        packages have booted, use the event system and listen to the booted event:
        self.events.listen('uvicore.foundation.events.app.Booted', self.booted)"""

        # Define Provider Registrations
        self.registers(self.package.config.registers)

        # Define Redis Connections
        self.register_redis_connections(
            connections=self.package.config.redis.connections,
            default=self.package.config.redis.default
        )

        # Define Database Connections
        self.register_db_connections(
            connections=self.package.config.database.connections,
            default=self.package.config.database.default
        )

        # Define all tables or models
        # The goal is to load up all SQLAlchemy tables for complete metedata definitions.
        # If you separate tables vs models use self.tables(['myapp.database.tables])
        # If you use models only, or models with inline tables then use self.models(['myapp.models])
        # Order does not matter as they are sorted topologically for ForeignKey dependencies
        # If you don't have an __init__.py index in your tables or models you can use
        # wildcard imports self.models(['myapp.models.*])
        self.register_db_models([
            'app1.models',
        ])
        self.register_db_tables([
            'app1.database.tables.*',
        ])

        # Define data seeders
        self.register_db_seeders([
            'app1.database.seeders.seed',
        ])

        # Define view and asset paths and configure the templating system
        self.register_views()

        # Define Web and API routes and prefixes
        self.register_routes()

        # Define CLI commands to be added to the ./uvicore command line interface
        self.register_commands()

    def register_views(self) -> None:
        """Register HTTP view and asset paths and configure the Web templating system"""

        # Define view paths
        self.register_http_views(['app1.http.views'])

        # Define view composers - multiple calls to self.composers() are appended
        #self.register_http_view_composers('mreschke.wiki.http.composers.layout.Layout', 'wiki/*')
        #self.register_http_view_composers('mreschke.wiki.http.composers.layout.Layout', ['wiki/home', 'wiki/about'])

        # You can also define view composers as a dict
        # self.register_http_view_composers({
        #     'mreschke.wiki.http.composers.layout.Layout': 'wiki/*',
        #     'mreschke.wiki.http.composers.layout.Layout': ['wiki/home', 'wiki/about'],
        # })

        # Define public paths
        self.register_http_public(['app1.http.publicc'])

        # Define asset paths
        self.register_http_assets(['app1.http.public.assets'])

        # Define custom template options
        # def url_method(context: dict, name: str, **path_params: any) -> str:
        #     request = context["request"]
        #     return request.url_for(name, **path_params)

        # def up_filter(input):
        #     return input.upper()

        # def up_filter2(context, input):
        #     return input.upper()

        # def is_prime(n):
        #     import math
        #     if n == 2:
        #         return True
        #     for i in range(2, int(math.ceil(math.sqrt(n))) + 1):
        #         if n % i == 0:
        #             return False
        #     return True

        # self.register_http_view_context_processors({
        #     'context_functions': {
        #         'url2': url_method,
        #     },
        #     'context_filters': {
        #         'up': up_filter2,
        #     },
        #     'filters': {
        #         'up': up_filter,
        #     },
        #     'tests': {
        #         'prime': is_prime,
        #     },
        # })
        # Optionally, hack jinja to add anything possible like so
        #app.jinja.env.globals['whatever'] = somefunc

    def register_routes(self) -> None:
        """Register Web and API routes and prefixes"""

        # Define web routes
        self.register_http_web_routes(
            module='app1.http.routes.web.Web',
            prefix=self.package.config.web.prefix,
            #name_prefix=None,
        )

        # Define api routes
        self.register_http_api_routes(
            module='app1.http.routes.api.Api',
            prefix=self.package.config.api.prefix,
            #name_prefix='api',
        )

    def register_commands(self) -> None:
        """Register CLI commands to be added to the ./uvicore command line interface"""

        # You can define CLI groups and commands as a complete dictionary
        # self.commands({
        #     'wiki': {
        #         'help': 'Wiki Commands',
        #         'commands': {
        #             'welcome': 'mreschke.wiki.commands.welcome.cli',
        #         },
        #     },
        # })

        # Or you can define commands as kwargs (multiple calls to self.commands() are appended)
        self.register_cli_commands(
            group='app1',
            help='App1 Commands',
            commands={
                'test': 'app1.commands.test.cli',
                'shell': 'app1.commands.shell.cli',
            }
        )
