from uvicore.support.provider import ServiceProvider


class Foundation(ServiceProvider):

    def register(self):

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

    def boot(self):
        # Register commands
        self.register_commands()



    def register_commands(self):
        # Register HTTP Serve commands
        self.commands([
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
        self.commands([
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
