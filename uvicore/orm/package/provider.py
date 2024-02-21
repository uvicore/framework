import uvicore
from typing import Dict
from uvicore.package import Provider
from uvicore.support.dumper import dump, dd
from uvicore.console.package.registers import Cli


@uvicore.provider()
class Orm(Provider, Cli):

    def register(self) -> None:
        """Register package into the uvicore framework.
        All packages are registered before the framework boots.  This is where
        you define your packages configs, IoC bindings and early event listeners.
        Configs are deep merged only after all packages are registered.  No real
        work should be performed here as it is very early in the bootstraping
        process and we have no clear view of the full configuration system."""

        # ???
        # Maybe provide a self.event_strings({}) to at least define which event strings there are
        # then you can show in ./uvicore event list

        # Register events used in this package
        # self.events.register(
        #     name='uvicore.orm-{dynamic.your.model}-BeforeSave',
        #     description='Dynamic, before saving (insert or update) model to db.',
        #     dynamic=True,
        #     is_async=True
        # )
        # self.events.register(
        #     name='uvicore.orm-{your.model}-AfterSave',
        #     description='Dynamic, after saving (insert or update) model to db.',
        #     dynamic=True,
        #     is_async=True,
        # )

        # {model} is would be full app1.models.post.Post
        # uvicore.orm-app1.models.post.Post-Saving

        # Listen to all ORM saving
        #orm-*-saving

        # Listen to all post model events
        #orm-{post}-*

        # def test(event, payload):
        #     print('hi')

        #dd(uvicore.events.event('uvicore.foundation.events.app.Registered'))

        # Register IoC bindings
        # Automatic - self.bind('Model', 'uvicore.orm.model._Model', aliases=['model'])
        # Automatic - self.bind('ModelMetaclass', 'uvicore.orm.metaclass._ModelMetaclass')

        #self.bind('Model', 'uvicore.orm.model._Model', aliases=['model'])
        #self.bind('ModelMetaclass', 'uvicore.orm.metaclass._ModelMetaclass')

    def boot(self) -> None:
        """Bootstrap package into the uvicore framework.
        Boot takes place after ALL packages are registered.  This means all package
        configs are deep merged to provide a complete and accurate view of all
        configuration. This is where you register, connections, models,
        views, assets, routes, commands...  If you need to perform work after ALL
        packages have booted, use the event system and listen to the booted event:
        self.events.listen('uvicore.foundation.events.app.Booted', self.booted)"""

        # Define service provider registration control
        self.registers(self.package.config.registers)

        # Define commands
        self.register_cli_commands({
            # Extend schematic generator commands
            'gen': {
                'commands': {
                    'model': 'uvicore.orm.commands.generators.model',
                },
            }
        })
