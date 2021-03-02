import uvicore
from typing import Dict
from uvicore.package import ServiceProvider
from uvicore.support.dumper import dump, dd
from uvicore.console.provider import Cli


@uvicore.provider()
class Orm(ServiceProvider, Cli):

    def register(self) -> None:

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

        def test(event, payload):
            print('hi')

        #dd(uvicore.events.event('uvicore.foundation.events.app.Registered'))

        # Register IoC bindings
        # Automatic - self.bind('Model', 'uvicore.orm.model._Model', aliases=['model'])
        # Automatic - self.bind('ModelMetaclass', 'uvicore.orm.metaclass._ModelMetaclass')

        #self.bind('Model', 'uvicore.orm.model._Model', aliases=['model'])
        #self.bind('ModelMetaclass', 'uvicore.orm.metaclass._ModelMetaclass')

    def boot(self) -> None:
        # Define service provider registration control
        self.registers(self.package.config.registers)

        # Define commands
        self.commands({
            # Extend schematic generator commands
            'gen': {
                'commands': {
                    'model': 'uvicore.orm.commands.generators.model',
                },
            }
        })
