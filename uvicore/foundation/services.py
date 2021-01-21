import uvicore
from uvicore.package import ServiceProvider
from uvicore.support.dumper import dump, dd
from uvicore.console.provider import Cli


@uvicore.provider()
class Foundation(ServiceProvider, Cli):

    def register(self):

        # Register configs
        self.configs([
            {'key': self.name, 'module': 'uvicore.foundation.config.package.config'}
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
        # Regster commands
        # self.commands([
        #     # Register Ioc commands
        #     {
        #         'group': {
        #             'name': 'ioc',
        #             'parent': 'root',
        #             'help': 'Uvicore Ioc (Inversion of Control) Information',
        #         },
        #         'commands': [
        #             {'name': 'bindings', 'module': 'uvicore.foundation.commands.ioc.bindings'},
        #             {'name': 'singletons', 'module': 'uvicore.foundation.commands.ioc.singletons'},
        #             {'name': 'overrides', 'module': 'uvicore.foundation.commands.ioc.overrides'},
        #             {'name': 'type', 'module': 'uvicore.foundation.commands.ioc.type'},
        #         ],
        #     },

        #     # Register Package commands
        #     {
        #         'group': {
        #             'name': 'package',
        #             'parent': 'root',
        #             'help': 'Uvicore Package Information',
        #         },
        #         'commands': [
        #             {'name': 'providers', 'module': 'uvicore.foundation.commands.package.providers'},
        #             {'name': 'list', 'module': 'uvicore.foundation.commands.package.list'},
        #             {'name': 'show', 'module': 'uvicore.foundation.commands.package.show'},
        #         ],
        #     },

        #     # Register Event commands
        #     {
        #         'group': {
        #             'name': 'event',
        #             'parent': 'root',
        #             'help': 'Uvicore Event Information',
        #         },
        #         'commands': [
        #             {'name': 'list', 'module': 'uvicore.events.commands.event.list'},
        #             {'name': 'show', 'module': 'uvicore.events.commands.event.show'},
        #         ],
        #     },
        # ])

        # NEW
        self.commands({
            # Register Ioc commands
            'ioc': {
                'help': 'Uvicore Ioc (Inversion of Control) Information',
                'commands': {
                    'bindings': 'uvicore.foundation.commands.ioc.bindings',
                    'singletons': 'uvicore.foundation.commands.ioc.singletons',
                    'overrides': 'uvicore.foundation.commands.ioc.overrides',
                    'type': 'uvicore.foundation.commands.ioc.type',
                },
            },

            # Register Package commands
            'package': {
                'help': 'Uvicore Package Information',
                'commands': {
                    'providers': 'uvicore.foundation.commands.package.providers',
                    'list': 'uvicore.foundation.commands.package.list',
                    'show': 'uvicore.foundation.commands.package.show',
                },
            },

            # Register Event commands
            'event': {
                'help': 'Uvicore Event Information',
                'commands': {
                    'list': 'uvicore.events.commands.event.list',
                    'show': 'uvicore.events.commands.event.show',
                },
            },
        })
