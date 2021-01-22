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
        # Define service provider registration control
        self.registers(self.package.config('registers'))

        # Define commands
        # Why here in foundation?  Because these items are not actual packages
        # with their own service providers to register themselves.
        self.commands({
            # Register Ioc commands
            'ioc': {
                'help': 'Uvicore Ioc (Inversion of Control) Information',
                'commands': {
                    'list': 'uvicore.container.commands.ioc.list',
                    'singletons': 'uvicore.container.commands.ioc.singletons',
                    'overrides': 'uvicore.container.commands.ioc.overrides',
                    'type': 'uvicore.container.commands.ioc.type',
                    'get': 'uvicore.container.commands.ioc.get',
                },
            },

            # Register Package commands
            'package': {
                'help': 'Uvicore Package Information',
                'commands': {
                    'providers': 'uvicore.package.commands.package.providers',
                    'list': 'uvicore.package.commands.package.list',
                    'get': 'uvicore.package.commands.package.get',
                },
            },

            # Register Event commands
            'event': {
                'help': 'Uvicore Event Information',
                'commands': {
                    'list': 'uvicore.events.commands.event.list',
                    'get': 'uvicore.events.commands.event.get',
                },
            },
        })
