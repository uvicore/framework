import uvicore
from uvicore.package import ServiceProvider
from uvicore.support.dumper import dump, dd


@uvicore.provider()
class App1(ServiceProvider):

    def register(self) -> None:
        # Register configs
        self.configs([
            {'key': self.name, 'module': 'app1.config.app1.config'},
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


        # Test bind overrides instead of app.config bindings array
        #self.bind_override('uvicore.auth.database.tables.users.Users', 'app1.database.tables.users.Users')
        #self.bind_override('uvicore.auth.models.user.User', 'app1.models.user.User')



    def boot(self) -> None:
        # Using __init__.py now so just import it
        from app1 import models
        # self.tables([
        #    'app1.database.tables.*',
        # ])

        #NO
        # self.models([
        #     'app1.models.*',
        # ])

        self.seeders([
            'app1.database.seeders.seeders.seed',
        ])

        # Define view and asset paths and configure the templating system
        # self.load_views()

        # Define Web and API routers
        self.load_routes()

        # Define CLI commands to be added to the ./uvicore command line interface
        self.load_commands()

    def load_views(self) -> None:
        """Define view and asset paths and configure the templating system
        """
        # Add view paths
        self.views(['mreschke.wiki.http.views'])

        # Add asset paths
        self.assets([
            'mreschke.wiki.http.static2', #foundation example - BLUE
            'mreschke.wiki.http.static',  # wiki override example - RED
        ])

        def url_method(context: dict, name: str, **path_params: any) -> str:
            request = context["request"]
            return request.url_for(name, **path_params)

        def up_filter(input):
            return input.upper()

        def up_filter2(context, input):
            return input.upper()

        def is_prime(n):
            import math
            if n == 2:
                return True
            for i in range(2, int(math.ceil(math.sqrt(n))) + 1):
                if n % i == 0:
                    return False
            return True

        # Add custom template options
        self.template({
            'context_functions': [
                {'name': 'url2', 'method': url_method}
            ],
            'context_filters': [
                {'name': 'up', 'method': up_filter2}
            ],
            'filters': [
                {'name': 'up', 'method': up_filter}
            ],
            'tests': [
                {'name': 'prime', 'method': is_prime}
            ],
        })
        # Optionally, hack jinja to add anything possible like so
        #app.jinja.env.globals['whatever'] = somefunc

    def load_routes(self) -> None:
        """Define Web and API router"""
        #self.web_routes('app1.http.routes.web.Web')
        self.api_routes('app1.http.routes.api.Api')

    def load_commands(self) -> None:
        """Define CLI commands to be added to the ./uvicore command line interface"""
        group = 'app1'
        self.commands([
            {
                'group': {
                    'name': group,
                    'parent': 'root',
                    'help': 'App1 Commands',
                },
                'commands': [
                    {'name': 'test', 'module': 'app1.commands.test.cli'},
                    {'name': 'shell', 'module': 'app1.commands.shell.cli'},
                ],
            },
            # {
            #     'group': {
            #         'name': 'db',
            #         'parent': group,
            #         'help': 'Wiki DB Commands',
            #     },
            #     'commands': [
            #         {'name': 'create', 'module': 'mreschke.wiki.commands.db.create'},
            #         {'name': 'drop', 'module': 'mreschke.wiki.commands.db.drop'},
            #         {'name': 'recreate', 'module': 'mreschke.wiki.commands.db.recreate'},
            #         {'name': 'seed', 'module': 'mreschke.wiki.commands.db.seed'},
            #     ],
            # }
        ])
