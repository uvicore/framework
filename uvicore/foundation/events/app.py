from uvicore import log
from uvicore.events import Event
from uvicore.support.dumper import dump, dd


class Registered(Event):

    def __init__(self, test: str):
        self.test = test

    def dispatch(self):
        # You can optionally do stuff before and after all listeners are dispatched
        print("--BEFORE registered event")
        super().dispatch()
        print("--AFTER registered event")


class Booted(Event):

    def __init__(self, test: str):
        self.test = test

    def dispatch(self):
        # You can optionally do stuff before and after all listeners are dispatched
        print("--BEFORE booted event")
        super().dispatch()
        print("--AFTER booted event")

