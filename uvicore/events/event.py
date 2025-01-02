import uvicore
from uvicore.support.dumper import dump, dd
from dataclasses import dataclass
from uvicore.typing import Dict, Optional, Union, Callable


@uvicore.service()
class Event():

    # Defaults
    is_async: bool = False

    @classmethod
    @property
    def name(cls):
        name = str(cls).split("'")[1]
        # print(name, 'aaa')
        # if name == 'uvicore.events.event.Event':
        #     name = cls.__module__ + '.' + cls.__name__
        #print(name, 'xxx')
        return name

    @classmethod
    @property
    def description(cls):
        return cls.__doc__

    @classmethod
    def listen(cls, handler: Union[str, Callable], *, priority: int = 50):
        """Listen to to this event using this handler"""
        uvicore.events.listen(cls, handler, priority=priority)

    @classmethod
    def listener(cls, handler: Union[str, Callable], *, priority: int = 50):
        """Alias to Listen"""
        uvicore.events.listen(cls, handler, priority=priority)

    @classmethod
    def handle(cls, handler: Union[str, Callable], *, priority: int = 50):
        """Alias to Listen"""
        uvicore.events.listen(cls, handler, priority=priority)

    @classmethod
    def handler(cls, handler: Union[str, Callable], *, priority: int = 50):
        """Alias to Listen"""
        uvicore.events.listen(cls, handler, priority=priority)

    @classmethod
    def call(cls, handler: Union[str, Callable], *, priority: int = 50):
        """Alias to Listen"""
        uvicore.events.listen(cls, handler, priority=priority)

    def dispatch(self):
        """Fire off an event and run all listener callbacks"""
        uvicore.events._dispatch(self)

    async def dispatch_async(self):
        """Async fire off an event and run all async listener callbacks."""
        await uvicore.events._dispatch_async(self)

    async def codispatch(self):
        """Async fire off an event and run all async listener callbacks.  Alias for dispatch_async()."""
        await uvicore.events._dispatch_async(self)


    # No, logging should be a listener
    # def log(self, cls):
    #     uvicore.log.debug("Event " + str(cls.__class__.__module__) + " Dispatched")

