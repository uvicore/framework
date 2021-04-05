import uvicore
from uvicore.events import Event


@uvicore.event()
class Startup(Event):
    """Console is starting up.  Runs before console command."""

    is_async = True

    def __init__(self):
        pass


@uvicore.event()
class Shutdown(Event):
    """Console is shutting down.  Runs after console command"""

    is_async = True

    def __init__(self):
        pass

