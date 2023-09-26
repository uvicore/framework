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
        # Register configs
        self.configs([
            {'key': self.name, 'module': 'app1.config.package.config'},
            {'key': 'uvicore.auth', 'module': 'app1.config.auth.config'},
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

        # Define Service Provider Registrations
        self.registers(self.package.config.registers)

        # Define Database Connections
        self.connections(
            connections=self.package.config.database.connections,
            default=self.package.config.database.default
        )

        # Define Redis Connections
        self.redis_connections(
            connections=self.package.config.redis.connections,
            default=self.package.config.redis.default
        )

        # Using __init__.py now so just import it
        #from app1 import models

        # Use self.tables only for code coverage
        self.tables([
           'app1.database.tables.*',
        ])

        self.models(['app1.models'])

        self.seeders(['app1.database.seeders.seed'])

        # Define view and asset paths and configure the templating system
        self.define_views()

        # Define Web and API routers
        self.define_routes()

        # Define CLI commands to be added to the ./uvicore command line interface
        self.define_commands()

    def define_views(self) -> None:
        """Define view and asset paths and configure the templating system
        """
        # Define view paths
        self.views(['app1.http.views'])

        # Define public paths
        self.public(['app1.http.public'])

        # Define asset paths
        self.assets(['app1.http.public.assets'])

    def define_routes(self) -> None:
        """Define Web and API router"""
        self.web_routes(
            module='app1.http.routes.web.Web',
            prefix=self.package.config.web.prefix,
            #name_prefix=None,
        )

        self.api_routes(
            module='app1.http.routes.api.Api',
            prefix=self.package.config.api.prefix,
            #name_prefix='api',
        )

    def define_commands(self) -> None:
        """Define CLI commands to be added to the ./uvicore command line interface"""
        self.commands(
            group='app1',
            help='App1 Commands',
            commands={
                'test': 'app1.commands.test.cli',
                'shell': 'app1.commands.shell.cli',
            }
        )
