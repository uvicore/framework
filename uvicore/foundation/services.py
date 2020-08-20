import uvicore
#from uvicore.support.provider import ServiceProvider
from uvicore.package import ServiceProvider
from uvicore.support.dumper import dump, dd


class Foundation(ServiceProvider):

    def register(self):

        # Register config
        self.configs([
            {'key': self.name, 'module': 'uvicore.foundation.config.foundation.config'}
        ])

        # Register events used in this package
        self.events.register({
            'uvicore.foundation.events.app.Registered': {
                'description': 'Application bootstrap has registered all package service providers',
                'type': 'class',
            },
            'uvicore.foundation.events.app.Booted': {
                'description': 'Application bootstrap has booted all package service providers',
                'type': 'class',
            },
        })

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

        # Register Event commands
        self.commands([
            {
                'group': {
                    'name': 'event',
                    'parent': 'root',
                    'help': 'Uvicore Event Information',
                },
                'commands': [
                    {'name': 'list', 'module': 'uvicore.events.commands.event.list'},
                    {'name': 'show', 'module': 'uvicore.events.commands.event.show'},
                ],
            }
        ])
