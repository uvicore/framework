import uvicore
from uvicore.package import ServiceProvider
from uvicore.support.dumper import dump, dd

@uvicore.provider()
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
        pass
        # Register Ioc commands
        self.commands([
            {
                'group': {
                    'name': 'ioc',
                    'parent': 'root',
                    'help': 'Uvicore Ioc (Inversion of Control) Information',
                },
                'commands': [
                    {'name': 'bindings', 'module': 'uvicore.foundation.commands.ioc.bindings'},
                    {'name': 'singletons', 'module': 'uvicore.foundation.commands.ioc.singletons'},
                    {'name': 'overrides', 'module': 'uvicore.foundation.commands.ioc.overrides'},
                    {'name': 'type', 'module': 'uvicore.foundation.commands.ioc.type'},
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
                    {'name': 'providers', 'module': 'uvicore.foundation.commands.package.providers'},
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
