"""
Event system test suite.

Organized into sections, each locking in a distinct behavior of the dispatcher
(uvicore/events/dispatcher.py) and the Event/Handler base classes
(uvicore/events/event.py, uvicore/events/handler.py):

    * String based events (loose Dict payload)
    * Class based events (strict constructor payload)
    * Handler types (function, async function, callable class, string path)
    * Listen aliases (listen/listener/handle/handler/call)
    * Decorator registration
    * Priority ordering
    * Multiple listeners / multiple events
    * Wildcard listeners
    * Subscriptions
    * Sync vs async dispatch semantics
    * Introspection (name, description, is_async, IoC registration, listeners)

Test isolation
--------------
uvicore.events is a session wide singleton, so listeners would normally leak
between tests.  The `events` fixture snapshots the dispatcher's listener registry
before each test and restores it afterwards, so every test starts from the real
(framework wired) registry and any listeners it adds are torn down cleanly.  This
keeps the suite order independent.

Module level classes
---------------------
The Event/Handler/Subscription classes used here live in `tests/event_fixtures.py`
rather than in this file.  They cannot be defined at this module's scope because
pytest imports test files during collection, before the application has
bootstrapped, and `@uvicore.event()` needs the IoC container.  The `fx` fixture
imports them lazily once `app1` has booted.  Module level classes also have
stable, importable dotted paths, which is what lets us exercise the dispatcher's
string-import handler path.
"""

import pytest
import uvicore
from uvicore.typing import Dict


# ==============================================================================
# Fixtures
# ==============================================================================

@pytest.fixture
def events(app1):
    """The global dispatcher with its listener registry isolated per test.

    Starts each test from a copy of the live registry (so framework wiring such
    as the database connect/disconnect listeners stay intact) and restores the
    originals on teardown.
    """
    from uvicore.typing import Dict as UDict
    dispatcher = uvicore.events

    orig_listeners = dispatcher._listeners
    orig_wildcards = dispatcher._wildcards

    # One level deep copy: new dict + new lists, listener callables shared by ref
    dispatcher._listeners = UDict({k: list(v) for k, v in orig_listeners.items()})
    dispatcher._wildcards = list(orig_wildcards)

    try:
        yield dispatcher
    finally:
        dispatcher._listeners = orig_listeners
        dispatcher._wildcards = orig_wildcards


@pytest.fixture
def fx(app1):
    """Lazily import the module level Event/Handler fixtures (post-bootstrap)."""
    from tests.test_events import event_fixtures
    return event_fixtures


# ==============================================================================
# String based events
# ==============================================================================

@pytest.mark.asyncio
async def test_string_event_sync_method(events):
    """A string event delivers a SuperDict merging payload + name + description."""
    received = {}

    def handle(event):
        received['event'] = event

    events.listen('evt.string', handle)
    events.dispatch('evt.string', {'stuff': 'here'})

    assert received['event'] == Dict({
        'stuff': 'here',
        'name': 'evt.string',
        'description': 'String based dynamic event.',
    })


@pytest.mark.asyncio
async def test_string_event_async_method(events):
    """Async string dispatch via codispatch fires async handlers."""
    received = {}

    async def handle(event):
        received['event'] = event

    events.listen('evt.string.async', handle)
    await events.codispatch('evt.string.async', {'stuff': 'here'})

    assert received['event'].stuff == 'here'
    assert received['event'].name == 'evt.string.async'


@pytest.mark.asyncio
async def test_string_event_payload_dot_access(events):
    """Payload keys are reachable via dot notation on the SuperDict event."""
    seen = {}

    def handle(event):
        seen['value'] = event.foo

    events.listen('evt.dot', handle)
    events.dispatch('evt.dot', {'foo': 'bar'})

    assert seen['value'] == 'bar'


@pytest.mark.asyncio
async def test_dispatch_with_no_listeners_is_noop(events):
    """Dispatching an event nobody listens to is a harmless no-op."""
    assert events.dispatch('evt.nobody', {'a': 1}) is None
    await events.codispatch('evt.nobody.async', {'a': 1})


# ==============================================================================
# Class based events
# ==============================================================================

@pytest.mark.asyncio
async def test_class_event_instance_dispatch(events, fx):
    """Event(...).dispatch() runs handlers with the event instance itself."""
    calls = []

    def handle(event):
        assert isinstance(event, fx.SampleEvent)
        event.calls.append('handled')

    fx.SampleEvent.listen(handle)
    fx.SampleEvent(calls).dispatch()

    assert calls == ['handled']


@pytest.mark.asyncio
async def test_class_event_global_dispatch(events, fx):
    """events.dispatch(instance) is equivalent to instance.dispatch()."""
    calls = []
    fx.SampleEvent.listen(lambda event: event.calls.append('global'))
    events.dispatch(fx.SampleEvent(calls))
    assert calls == ['global']


@pytest.mark.asyncio
async def test_class_event_async_codispatch(events, fx):
    """An async event dispatched with codispatch runs async handlers."""
    calls = []

    async def handle(event):
        event.calls.append('async-handled')

    fx.AsyncSampleEvent.listen(handle)
    await fx.AsyncSampleEvent(calls).codispatch()

    assert calls == ['async-handled']


@pytest.mark.asyncio
async def test_class_event_dispatch_by_class_string(events, fx):
    """Dispatching a string that matches a class path auto-instantiates the class.

    The handler must receive a real SampleEvent instance (not a SuperDict),
    constructed from the payload as **kwargs.
    """
    calls = []

    def handle(event):
        assert isinstance(event, fx.SampleEvent)
        assert event.value == 42
        event.calls.append('by-string')

    events.listen(fx.SampleEvent, handle)
    events.dispatch('tests.test_events.event_fixtures.SampleEvent', {'calls': calls, 'value': 42})

    assert calls == ['by-string']


@pytest.mark.asyncio
async def test_class_event_listen_via_class_object(events, fx):
    """events.listen(EventClass, handler) accepts the class object directly."""
    calls = []
    events.listen(fx.SampleEvent, lambda event: event.calls.append('via-class'))
    fx.SampleEvent(calls).dispatch()
    assert calls == ['via-class']


# ==============================================================================
# Handler types
# ==============================================================================

@pytest.mark.asyncio
async def test_handler_function(events, fx):
    calls = []
    fx.SampleEvent.listen(fx.append_fn)
    fx.SampleEvent(calls).dispatch()
    assert calls == ['append_fn']


@pytest.mark.asyncio
async def test_handler_async_function(events, fx):
    calls = []
    fx.AsyncSampleEvent.listen(fx.append_fn_async)
    await fx.AsyncSampleEvent(calls).codispatch()
    assert calls == ['append_fn_async']


@pytest.mark.asyncio
async def test_handler_callable_class(events, fx):
    """A Handler subclass with __call__ is instantiated then invoked."""
    calls = []
    fx.SampleEvent.listen(fx.AppendHandler)
    fx.SampleEvent(calls).dispatch()
    assert calls == ['AppendHandler']


@pytest.mark.asyncio
async def test_handler_async_callable_class(events, fx):
    calls = []
    fx.AsyncSampleEvent.listen(fx.AsyncAppendHandler)
    await fx.AsyncSampleEvent(calls).codispatch()
    assert calls == ['AsyncAppendHandler']


@pytest.mark.asyncio
async def test_handler_string_path_to_class(events, fx):
    """A handler given as a dotted string is imported and instantiated."""
    calls = []
    events.listen(fx.SampleEvent, 'tests.test_events.event_fixtures.AppendHandler')
    fx.SampleEvent(calls).dispatch()
    assert calls == ['AppendHandler']


@pytest.mark.asyncio
async def test_handler_string_path_async(events, fx):
    calls = []
    events.listen(fx.AsyncSampleEvent, 'tests.test_events.event_fixtures.AsyncAppendHandler')
    await fx.AsyncSampleEvent(calls).codispatch()
    assert calls == ['AsyncAppendHandler']


@pytest.mark.asyncio
async def test_bad_string_handler_is_skipped(events, fx):
    """A handler string that can't be imported is silently skipped; siblings still fire."""
    calls = []
    events.listen(fx.SampleEvent, 'does.not.Exist')     # bad, should be skipped
    events.listen(fx.SampleEvent, fx.append_fn)         # good, must still fire
    fx.SampleEvent(calls).dispatch()
    assert calls == ['append_fn']


# ==============================================================================
# Listen aliases
# ==============================================================================

@pytest.mark.asyncio
async def test_dispatcher_listen_aliases_all_register(events):
    """listen/listener/handle/handler/call all register a listener on the dispatcher."""
    calls = []
    events.listen('evt.alias', lambda e: calls.append('listen'))
    events.listener('evt.alias', lambda e: calls.append('listener'))
    events.handle('evt.alias', lambda e: calls.append('handle'))
    events.handler('evt.alias', lambda e: calls.append('handler'))
    events.call('evt.alias', lambda e: calls.append('call'))

    events.dispatch('evt.alias')

    assert sorted(calls) == ['call', 'handle', 'handler', 'listen', 'listener']


@pytest.mark.asyncio
async def test_event_class_listen_aliases_all_register(events, fx):
    """The Event class exposes the same five aliases."""
    calls = []
    fx.SampleEvent.listen(lambda e: e.calls.append('listen'))
    fx.SampleEvent.listener(lambda e: e.calls.append('listener'))
    fx.SampleEvent.handle(lambda e: e.calls.append('handle'))
    fx.SampleEvent.handler(lambda e: e.calls.append('handler'))
    fx.SampleEvent.call(lambda e: e.calls.append('call'))

    fx.SampleEvent(calls).dispatch()

    assert sorted(calls) == ['call', 'handle', 'handler', 'listen', 'listener']


# ==============================================================================
# Decorator registration
# ==============================================================================

@pytest.mark.asyncio
async def test_decorator_listen_registers_and_returns_func(events):
    """Used as a decorator, listen() wires the handler and returns it unchanged."""
    calls = []

    @events.listen('evt.deco')
    def handle(event):
        calls.append('deco')

    assert handle.__name__ == 'handle'        # returned unchanged
    events.dispatch('evt.deco')
    assert calls == ['deco']


@pytest.mark.asyncio
async def test_decorator_handle_async(events):
    calls = []

    @events.handle('evt.deco.async')
    async def handle(event):
        calls.append('deco-async')

    await events.codispatch('evt.deco.async')
    assert calls == ['deco-async']


# ==============================================================================
# Priority ordering
# ==============================================================================

@pytest.mark.asyncio
async def test_priority_lower_runs_first(events):
    """Listeners run sorted by priority ascending."""
    calls = []
    events.listen('evt.prio', lambda e: calls.append('p90'), priority=90)
    events.listen('evt.prio', lambda e: calls.append('p10'), priority=10)
    events.listen('evt.prio', lambda e: calls.append('p50'), priority=50)

    events.dispatch('evt.prio')

    assert calls == ['p10', 'p50', 'p90']


@pytest.mark.asyncio
async def test_priority_default_is_50_and_stable(events):
    """Default priority is 50; equal priorities preserve registration order."""
    calls = []
    events.listen('evt.prio2', lambda e: calls.append('default-a'))            # 50
    events.listen('evt.prio2', lambda e: calls.append('explicit-10'), priority=10)
    events.listen('evt.prio2', lambda e: calls.append('default-b'))            # 50

    events.dispatch('evt.prio2')

    # 10 first, then the two defaults in the order they were registered
    assert calls == ['explicit-10', 'default-a', 'default-b']


# ==============================================================================
# Multiple listeners / multiple events
# ==============================================================================

@pytest.mark.asyncio
async def test_multiple_listeners_all_fire(events):
    calls = []
    events.listen('evt.multi', lambda e: calls.append('one'))
    events.listen('evt.multi', lambda e: calls.append('two'))
    events.listen('evt.multi', lambda e: calls.append('three'))

    events.dispatch('evt.multi')

    assert calls == ['one', 'two', 'three']


@pytest.mark.asyncio
async def test_listen_multiple_events_with_list(events):
    """A single listen([...]) call wires one handler to several events."""
    calls = []
    events.listen(['evt.a', 'evt.b'], lambda e: calls.append(e.name))

    events.dispatch('evt.a')
    events.dispatch('evt.b')

    assert calls == ['evt.a', 'evt.b']


@pytest.mark.asyncio
async def test_dispatching_twice_fires_twice(events):
    calls = []
    events.listen('evt.twice', lambda e: calls.append('x'))
    events.dispatch('evt.twice')
    events.dispatch('evt.twice')
    assert calls == ['x', 'x']


# ==============================================================================
# Wildcard listeners
# ==============================================================================

@pytest.mark.asyncio
async def test_wildcard_trailing(events):
    """A trailing * matches any event under that prefix."""
    calls = []
    events.listen('evt.wild.*', lambda e: calls.append('wild'))
    events.dispatch('evt.wild.Something')
    assert calls == ['wild']


@pytest.mark.asyncio
async def test_wildcard_middle(events):
    """A * also matches in the middle of an event name."""
    calls = []
    events.listen('evt.model.*.Deleted', lambda e: calls.append('deleted'))

    events.dispatch('evt.model.Post.Deleted')   # matches
    events.dispatch('evt.model.Post.Created')   # no match

    assert calls == ['deleted']


@pytest.mark.asyncio
async def test_wildcard_registered_in_wildcards_list(events, fx):
    """Listening to a wildcard event records it in the dispatcher's wildcard list."""
    events.listen('evt.tracked.*', fx.append_fn)
    assert 'evt.tracked.*' in events.wildcards


@pytest.mark.asyncio
async def test_wildcard_and_exact_listeners_both_fire(events):
    """An exact listener and a matching wildcard listener both run."""
    calls = []
    events.listen('evt.both.Created', lambda e: calls.append('exact'))
    events.listen('evt.both.*', lambda e: calls.append('wild'))

    events.dispatch('evt.both.Created')

    assert sorted(calls) == ['exact', 'wild']


# ==============================================================================
# Subscriptions
# ==============================================================================

@pytest.mark.asyncio
async def test_subscribe_instance(events, fx):
    """subscribe(instance) calls the instance's subscribe() to wire its listeners."""
    calls = []
    events.subscribe(fx.SampleSubscription())

    fx.SampleEvent(calls).dispatch()
    await fx.AsyncSampleEvent(calls).codispatch()

    assert calls == ['on_sample', 'on_async_sample']


@pytest.mark.asyncio
async def test_subscribe_string_path(events, fx):
    """subscribe('dotted.path') imports, instantiates and wires the subscription."""
    calls = []
    events.subscribe('tests.test_events.event_fixtures.SampleSubscription')

    fx.SampleEvent(calls).dispatch()
    await fx.AsyncSampleEvent(calls).codispatch()

    assert calls == ['on_sample', 'on_async_sample']


@pytest.mark.asyncio
async def test_subscribe_bad_string_path_is_skipped(events):
    """A subscription string that can't be imported is swallowed, not raised."""
    events.subscribe('does.not.Exist')   # must not raise


# ==============================================================================
# Sync vs async dispatch semantics
# ==============================================================================

@pytest.mark.asyncio
async def test_sync_handler_under_async_dispatch(events, fx):
    """A plain sync handler dispatched asynchronously runs (via threadpool)."""
    calls = []

    def sync_handler(event):
        event.calls.append('sync-in-async')

    events.listen(fx.AsyncSampleEvent, sync_handler)
    await fx.AsyncSampleEvent(calls).codispatch()

    assert calls == ['sync-in-async']


@pytest.mark.asyncio
async def test_mixed_sync_and_async_handlers_under_async_dispatch(events):
    """Async dispatch happily runs a mix of sync and async handlers."""
    calls = []

    def sync_handler(event):
        calls.append('sync')

    async def async_handler(event):
        calls.append('async')

    events.listen('evt.mixed', sync_handler)
    events.listen('evt.mixed', async_handler)

    await events.codispatch('evt.mixed')

    assert calls == ['sync', 'async']


@pytest.mark.asyncio
async def test_dispatch_async_equals_codispatch(events):
    """codispatch is a straight alias of dispatch_async."""
    calls = []
    events.listen('evt.alias.async', lambda e: calls.append('hit'))

    await events.dispatch_async('evt.alias.async')
    await events.codispatch('evt.alias.async')

    assert calls == ['hit', 'hit']


# ==============================================================================
# Introspection (name, description, is_async, IoC registration, listeners)
# ==============================================================================

@pytest.mark.asyncio
async def test_event_name_property(events, fx):
    """Event.name is the fully qualified class path."""
    assert fx.SampleEvent.name == 'tests.test_events.event_fixtures.SampleEvent'
    assert fx.SampleEvent().name == 'tests.test_events.event_fixtures.SampleEvent'


@pytest.mark.asyncio
async def test_event_description_property(events, fx):
    """Event.description is the class docstring."""
    assert fx.SampleEvent.description == 'A sample synchronous event.'


@pytest.mark.asyncio
async def test_is_async_flag(events, fx):
    """is_async defaults to False and reflects the declared value."""
    from uvicore.events import Event

    class PlainEvent(Event):
        def __init__(self):
            pass

    assert PlainEvent.is_async is False
    assert fx.SampleEvent.is_async is False
    assert fx.AsyncSampleEvent.is_async is True


@pytest.mark.asyncio
async def test_registered_events_includes_decorated(events, fx):
    """@uvicore.event() binds the class into the IoC, surfacing it in registered_events."""
    registered = {e['name']: e for e in events.registered_events}

    assert 'tests.test_events.event_fixtures.SampleEvent' in registered
    assert registered['tests.test_events.event_fixtures.SampleEvent']['is_async'] is False
    assert registered['tests.test_events.event_fixtures.SampleEvent']['description'] == 'A sample synchronous event.'

    assert 'tests.test_events.event_fixtures.AsyncSampleEvent' in registered
    assert registered['tests.test_events.event_fixtures.AsyncSampleEvent']['is_async'] is True


@pytest.mark.asyncio
async def test_listeners_property_structure(events, fx):
    """The listeners registry stores {'listener', 'priority'} entries per event."""
    events.listen('evt.struct', fx.append_fn, priority=70)
    assert events.listeners['evt.struct'] == [{'listener': fx.append_fn, 'priority': 70}]


@pytest.mark.asyncio
async def test_event_listeners_returns_handlers_sorted_by_priority(events):
    """event_listeners() returns just the handlers, sorted by priority ascending."""
    def a(event): pass
    def b(event): pass
    def c(event): pass

    events.listen('evt.sorted', a, priority=90)
    events.listen('evt.sorted', b, priority=10)
    events.listen('evt.sorted', c, priority=50)

    assert events.event_listeners('evt.sorted') == [b, c, a]


@pytest.mark.asyncio
async def test_event_listeners_includes_wildcard_matches(events):
    """event_listeners() folds in any wildcard listeners that match the event name."""
    def exact(event): pass
    def wild(event): pass

    events.listen('evt.fold.Created', exact)
    events.listen('evt.fold.*', wild)

    handlers = events.event_listeners('evt.fold.Created')
    assert exact in handlers
    assert wild in handlers


# ==============================================================================
# Isolation guard
# ==============================================================================

@pytest.mark.asyncio
async def test_listener_registry_is_isolated_between_tests(events):
    """Listeners added in other tests must not leak into this one.

    Every other test registered listeners on its own `evt.*` names; none of those
    should survive into this fixture-reset registry.
    """
    leaked = [name for name in events.listeners if name.startswith('evt.')]
    assert leaked == []
