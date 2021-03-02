import uvicore
from uvicore.package import ServiceProvider
from uvicore.support.dumper import dump, dd
from uvicore.console.provider import Cli

@uvicore.provider()
class Configuration(ServiceProvider, Cli):

    def register(self) -> None:
        """Register package into uvicore framework.
        All packages are registered before the framework boots.  This is where
        you define your packages configs and IoC bindings.  Configs are deep merged only after
        all packages are registered.  No real work should be performed here as it
        is very early in the bootstraping process and most internal processes are not
        instantiated yet."""

        # Register IoC bindings
        # self.bind('Configuration', 'uvicore.configuration.configuration._Configuration',
        #     aliases=['Config', 'config'],
        #     singleton=True,
        # )

        # Register configuration system
        self.register_configuration()

    def boot(self) -> None:
        """Bootstrap package into uvicore framework.
        Boot takes place after all packages are registered.  This means all package
        configs are deep merged to provide a complete and accurate view of all configs.
        This is where you load views, assets, routes, commands..."""

        # Define service provider registration control
        # No - Never allow this packages registrations to be disabled from other configs

        # Define commands
        self.commands(
            group='config',
            help='Configuration Information',
            commands={
                'list': 'uvicore.configuration.commands.config.list',
                'get': 'uvicore.configuration.commands.config.get',
            }
        )

    def register_configuration(self) -> None:
        # Set uvicore.log global
        uvicore.config = uvicore.ioc.make('uvicore.configuration.configuration.Configuration')

        # Set app.config for convenience (only after register since config is a service provider itself)
        # No, don't want duplicate entry points everywhere
        #self.app._config = uvicore.config

        # Set main app config
        uvicore.config.app = self.app_config
