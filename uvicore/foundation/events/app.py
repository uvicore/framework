import uvicore
from uvicore.events import Event


@uvicore.event()
class Registered(Event):
    """Application bootstrap has registered all package service providers."""

    is_async = False

    def __init__(self):
        self.x = 'x here'
        pass


@uvicore.event()
class Booted(Event):
    """Application bootstrap has booted all package service providers."""

    is_async = False

    def __init__(self):
        pass


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
