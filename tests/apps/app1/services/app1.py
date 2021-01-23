import uvicore
from uvicore.package import ServiceProvider
from uvicore.http.provider import Http
from uvicore.database.provider import Db
from uvicore.console.provider import Cli
from uvicore.support.dumper import dump, dd


@uvicore.provider()
class App1(ServiceProvider, Cli, Db, Http):

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
        # before this provider even hits.
        #self.bind_override('uvicore.foundation.application._Application', 'app1.overrides.application.Application')
        #self.bind_override('uvicore.package.Package', 'app1.overrides.package.Package')



        # Test bind overrides instead of app.config bindings array
        self.bind_override('uvicore.auth.database.tables.users.Users', 'app1.database.tables.users.Users')
        self.bind_override('uvicore.auth.models.user.User', 'app1.models.user.User')


    def boot(self) -> None:

        # Define Service Provider Registrations
        self.registers(self.package.config.registers)

        # Define Database Connections
        self.connections(self.package.config.database.connections, self.package.config.database.default)

        # Using __init__.py now so just import it
        #from app1 import models
        # self.tables([
        #    'app1.database.tables.*',
        # ])
        self.models([
            'app1.models',
        ])

        self.seeders([
            'app1.database.seeders.seeders.seed',
        ])

        # Define view and asset paths and configure the templating system
        # self.define_views()

        # Define Web and API routers
        self.define_routes()

        # Define CLI commands to be added to the ./uvicore command line interface
        self.define_commands()

    def define_views(self) -> None:
        """Define view and asset paths and configure the templating system
        """
        # Add view paths
        self.views(['mreschke.wiki.http.views'])

        # Add asset paths
        self.assets([
            'mreschke.wiki.http.static2', #foundation example - BLUE
            'mreschke.wiki.http.static',  # wiki override example - RED
        ])

    def define_routes(self) -> None:
        """Define Web and API router"""
        self.api_routes(
            module='app1.http.routes.api.Api',
            prefix=self.package.config.route.api_prefix
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
