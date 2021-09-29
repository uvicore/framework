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
        # self.events.register(
        #     name='uvicore.foundation.events.app.Registered',
        #     description='Application bootstrap has registered all package service providers.',
        #     dynamic=False,
        #     is_async=False,
        # )
        # self.events.register(
        #     name='uvicore.foundation.events.app.Booted',
        #     description='Application bootstrap has booted all package service providers.',
        #     dynamic=False,
        #     is_async=False,
        # )

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
        # No - Never allow this packages registrations to be disabled from other configs

        # Define commands
        # Why here in foundation?  Because these items are not actual packages
        # with their own service providers to register themselves.
        # self.commands({
        #     # Register Ioc commands
        #     'ioc': {
        #         'help': 'Uvicore Ioc (Inversion of Control) Information',
        #         'commands': {
        #             'bindings': 'uvicore.container.commands.ioc.bindings',
        #             'singletons': 'uvicore.container.commands.ioc.singletons',
        #             'overrides': 'uvicore.container.commands.ioc.overrides',
        #             'type': 'uvicore.container.commands.ioc.type',
        #             'get': 'uvicore.container.commands.ioc.get',
        #         },
        #     },

        #     # Register Package commands
        #     'package': {
        #         'help': 'Uvicore Package Information',
        #         'commands': {
        #             'providers': 'uvicore.package.commands.package.providers',
        #             'list': 'uvicore.package.commands.package.list',
        #             'get': 'uvicore.package.commands.package.get',
        #         },
        #     },

        #     # Register Event commands
        #     'event': {
        #         'help': 'Uvicore Event Information',
        #         'commands': {
        #             'list': 'uvicore.events.commands.event.list',
        #             'get': 'uvicore.events.commands.event.get',
        #             'listeners': 'uvicore.events.commands.event.listeners',
        #         },
        #     },
        # })

        # Alternative in kwargs format

        # Register App commands
        self.commands(
            group='app',
            help='Uvicore Application Information',
            commands={
                'info': 'uvicore.foundation.commands.app.info',
            }
        )


        # Register Ioc commands
        self.commands(
            group='ioc',
            help='Uvicore Ioc (Inversion of Control) Information',
            commands={
                'bindings': 'uvicore.container.commands.ioc.bindings',
                'singletons': 'uvicore.container.commands.ioc.singletons',
                'overrides': 'uvicore.container.commands.ioc.overrides',
                'type': 'uvicore.container.commands.ioc.type',
                'get': 'uvicore.container.commands.ioc.get',
            }
        )

        # Register Package commands
        self.commands(
            group='package',
            help='Uvicore Package Information',
            commands={
                'providers': 'uvicore.package.commands.package.providers',
                'list': 'uvicore.package.commands.package.list',
                'get': 'uvicore.package.commands.package.get',
            }
        )

        # Register Event commands
        self.commands(
            group='event',
            help='Uvicore Event Information',
            commands={
                'list': 'uvicore.events.commands.event.list',
                'get': 'uvicore.events.commands.event.get',
                'listeners': 'uvicore.events.commands.event.listeners',
            },
        )

        # Alternative, pull from a config
        #self.commands(self.package.config.commands)
