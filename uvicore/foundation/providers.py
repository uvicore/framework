from uvicore.support.provider import ServiceProvider


class Foundation(ServiceProvider):

    def register(self, app):

        # Register config
        self.configs([
            {'key': 'uvicore.foundation', 'module': 'uvicore.foundation.config.foundation.config'}
        ])

        # # Register root level commands
        # self.commands(
        #     name='root',
        #     #help='xx',
        #     commands=[
        #         ('version', 'uvicore.foundation.commands.version.cli'),
        #     ]
        # )

    def boot(self, app, package):
        # Register commands
        self.register_commands(package)



    def register_commands(self, package):
        # Register HTTP Serve commands
        self.commands(package, [
            {
                'group': {
                    'name': 'http',
                    'parent': 'root',
                    'help': 'Uvicore HTTP Commands',
                },
                'commands': [
                    {'name': 'serve', 'module': 'uvicore.foundation.commands.serve.cli'},
                ],
            }
        ])

        # Register Package commands
        self.commands(package, [
            {
                'group': {
                    'name': 'package',
                    'parent': 'root',
                    'help': 'Uvicore Package Information',
                },
                'commands': [
                    {'name': 'list', 'module': 'uvicore.foundation.commands.package.list'},
                    {'name': 'show', 'module': 'uvicore.foundation.commands.package.show'},
                ],
            }
        ])
