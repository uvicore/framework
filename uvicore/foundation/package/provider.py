import uvicore
from uvicore.package import Provider
from uvicore.support.dumper import dump, dd
from uvicore.console.package.registers import Cli


@uvicore.provider()
class Foundation(Provider, Cli):

    def register(self):
        """Register package into the uvicore framework.
        All packages are registered before the framework boots.  This is where
        you define your packages configs, IoC bindings and early event listeners.
        Configs are deep merged only after all packages are registered.  No real
        work should be performed here as it is very early in the bootstraping
        process and we have no clear view of the full configuration system."""

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
        """Bootstrap package into the uvicore framework.
        Boot takes place after ALL packages are registered.  This means all package
        configs are deep merged to provide a complete and accurate view of all
        configuration. This is where you register, connections, models,
        views, assets, routes, commands...  If you need to perform work after ALL
        packages have booted, use the event system and listen to the booted event:
        self.events.listen('uvicore.foundation.events.app.Booted', self.booted)"""

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
        self.register_cli_commands(
            group='app',
            help='Uvicore Application Information',
            commands={
                'info': 'uvicore.foundation.commands.app.info',
            }
        )


        # Register Ioc commands
        self.register_cli_commands(
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
        self.register_cli_commands(
            group='package',
            help='Uvicore Package Information',
            commands={
                'providers': 'uvicore.package.commands.package.providers',
                'list': 'uvicore.package.commands.package.list',
                'get': 'uvicore.package.commands.package.get',
            }
        )

        # Register Event commands
        self.register_cli_commands(
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
