import uvicore
from uvicore.package import Provider
from uvicore.support.dumper import dump, dd
from uvicore.console.package.registers import Cli


@uvicore.provider()
class Configuration(Provider, Cli):

    def register(self) -> None:
        """Register package into the uvicore framework.
        All packages are registered before the framework boots.  This is where
        you define your packages configs, IoC bindings and early event listeners.
        Configs are deep merged only after all packages are registered.  No real
        work should be performed here as it is very early in the bootstraping
        process and we have no clear view of the full configuration system."""

        # Register IoC bindings
        # self.bind('Configuration', 'uvicore.configuration.configuration._Configuration',
        #     aliases=['Config', 'config'],
        #     singleton=True,
        # )

        # Set uvicore.log global
        uvicore.config = uvicore.ioc.make('uvicore.configuration.configuration.Configuration')

        # Set app.config for convenience (only after register since config is a service provider itself)
        # No, don't want duplicate entry points everywhere
        #self.app._config = uvicore.config

        # Set main app config
        uvicore.config.app = self.app_config

    def boot(self) -> None:
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
        self.register_cli_commands(
            group='config',
            help='Configuration Information',
            commands={
                'list': 'uvicore.configuration.commands.config.list',
                'get': 'uvicore.configuration.commands.config.get',
            }
        )
