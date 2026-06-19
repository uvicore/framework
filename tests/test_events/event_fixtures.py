"""
Module level Event / Handler / Subscription classes for the event test suite.

This module is intentionally NOT a `test_*.py` file, so pytest does not import it
during collection.  That matters because `@uvicore.event()` (and the
`@uvicore.service()` on the Event base class) need the IoC container, which only
exists after the application has bootstrapped.  The event test suite imports this
module lazily, from a fixture that depends on the bootstrapped `app1`.

Because these classes live at module scope they have stable, importable dotted
paths (e.g. `tests.test_events.event_fixtures.AppendHandler`), which is required
to exercise the string-import handler path of the dispatcher.

Handlers record into `event.calls` (a list carried on the event payload) so the
tests can observe what fired, in what order, without any shared module state.
"""

import uvicore
from uvicore.events import Event, Handler


# ------------------------------------------------------------------------------
# Events
# ------------------------------------------------------------------------------

@uvicore.event()
class SampleEvent(Event):
    """A sample synchronous event."""

    is_async = False

    def __init__(self, calls=None, value=None):
        self.calls = calls if calls is not None else []
        self.value = value


@uvicore.event()
class AsyncSampleEvent(Event):
    """A sample asynchronous event."""

    is_async = True

    def __init__(self, calls=None, value=None):
        self.calls = calls if calls is not None else []
        self.value = value


# ------------------------------------------------------------------------------
# Handlers
# ------------------------------------------------------------------------------

class AppendHandler(Handler):
    """Sync handler class.  Appends its name to event.calls."""
    def __call__(self, event):
        event.calls.append('AppendHandler')


class AsyncAppendHandler(Handler):
    """Async handler class.  Appends its name to event.calls."""
    async def __call__(self, event):
        event.calls.append('AsyncAppendHandler')


def append_fn(event):
    """Module level sync function handler."""
    event.calls.append('append_fn')


async def append_fn_async(event):
    """Module level async function handler."""
    event.calls.append('append_fn_async')


# ------------------------------------------------------------------------------
# Subscription
# ------------------------------------------------------------------------------

class SampleSubscription:
    """All-in-one subscription.  It listens to this module's class based events so
    each handler receives the real event instance and can record into event.calls.
    The class needs no constructor state, so it can also be loaded by string path."""

    def on_sample(self, event):
        event.calls.append('on_sample')

    def on_async_sample(self, event):
        event.calls.append('on_async_sample')

    def subscribe(self, events):
        events.listen(SampleEvent, self.on_sample)
        events.listen(AsyncSampleEvent, self.on_async_sample)
