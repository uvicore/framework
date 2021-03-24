import uvicore
from uvicore.events import Event


@uvicore.event()
class Startup(Event):
    """HTTP Server has been started.  This is the Starlette startup async event."""

    is_async = True

    def __init__(self):

        pass


@uvicore.event()
class Shutdown(Event):
    """HTTP Server has been shutdown.  This is the Starlette shutdown async event."""

    is_async = True

    def __init__(self):
        self.is_async = True
        pass





# # Register events used in this package
# self.events.register(
#     name='uvicore.http.events.server.Startup',
#     description='HTTP Server has been started.  This is the Starlette startup event.',
#     is_async=False,
# )
# self.events.register(
#     name='uvicore.http.events.server.Shutdown',
#     description='HTTP Server has been shutdown.  This is the Starlette shutdown event.',
#     is_async=False,
# )
