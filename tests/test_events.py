import pytest
import uvicore
from uvicore.typing import Dict, List
from uvicore.support.dumper import dump


# @pytest.mark.asyncio
# @pytest.fixture(scope="module")
# async def app1(app1):
#     pass


@pytest.mark.asyncio
async def test1(app1):
    """Sync - String event, method handler, Dict payload"""

    # Event Handler
    x = 0
    def handle(event: Dict):
        nonlocal x; x = 1
        assert event == Dict({
            'stuff': 'here',
            'name': 'test1',
            'description': 'String based dynamic event.'
        })

    # Event Listener
    uvicore.events.listen('test1', handle)

    # Event Dispatcher
    uvicore.events.dispatch('test1', {'stuff': 'here'})

    assert x == 1


@pytest.mark.asyncio
async def test2(app1):
    """Sync - Class event, method handler, Class payload"""
    from uvicore.events import Event

    # Event
    class Test2(Event):
        def __init__(self, foo, bar):
            self.foo = foo
            self.bar = bar

    # Event Handler
    x = 0
    def handle(event: Test2):
        nonlocal x; x = 1
        assert event.__dict__ == {'foo': 'foohere', 'bar': 'barhere'}

    # Event Listener
    uvicore.events.listen('tests.test_events.test2.<locals>.Test2', handle)

    # Event Dispatcher
    uvicore.events.dispatch(Test2('foohere', 'barhere'))

    assert x == 1


@pytest.mark.asyncio
async def test3(app1):
    """Sync - Class event, decorator handler, Class payload"""
    from uvicore.events import Event

    # Event
    class Test3(Event):
        def __init__(self, foo, bar):
            self.foo = foo
            self.bar = bar

    # Event Listener and Handler
    #@uvicore.events.handle('tests.test_events.test3.<locals>.Test3')
    x = 0
    @uvicore.events.listen('tests.test_events.test3.<locals>.Test3')
    def handle(event: Test3):
        nonlocal x; x = 1
        assert event.__dict__ == {'foo': 'foohere', 'bar': 'barhere'}

    # Event Dispatcher
    #uvicore.events.dispatch(Test3('foohere', 'barhere'))
    Test3('foohere', 'barhere').dispatch()

    assert x == 1


@pytest.mark.asyncio
async def test4(app1):
    """Sync - Class event, method handler, Class payload, no strings"""
    from uvicore.events import Event

    # Event
    class Test4(Event):
        def __init__(self, foo, bar):
            self.foo = foo
            self.bar = bar

    # Event Listener and Handler
    x = 0
    def handle(event: Test4):
        nonlocal x; x = 1
        assert event.__dict__ == {'foo': 'foohere', 'bar': 'barhere'}

    # Event Listener
    #uvicore.events.listen(Test4, handle)
    Test4.listen(handle)

    # Event Dispatcher
    #uvicore.events.dispatch(Test3('foohere', 'barhere'))
    Test4('foohere', 'barhere').dispatch()

    assert x == 1


@pytest.mark.asyncio
async def test5(app1):
    """Sync - Class event, class handler, Class payload, no strings"""
    from uvicore.events import Event, Handler

    # Event
    class Test5(Event):
        def __init__(self, foo, bar):
            self.foo = foo
            self.bar = bar

    # Event Handler
    x = 0
    class Test5Handler(Handler):
        def __call__(self, event: Test5):
            nonlocal x; x = 1
            assert event.__dict__ == {'foo': 'foohere', 'bar': 'barhere'}

    # Event Listener
    #uvicore.events.listen(Test4, handle)
    Test5.call(Test5Handler)  # .listen, .listener, .handle, .handler, .call are all the same

    # Event Dispatcher
    uvicore.events.dispatch(Test5('foohere', 'barhere'))

    assert x == 1


@pytest.mark.asyncio
async def test6(app1):
    """Sync - Class event, class handler, Class payload"""
    from uvicore.events import Event, Handler

    # Event
    class Test6(Event):
        def __init__(self, foo, bar):
            self.foo = foo
            self.bar = bar

    # Event Handler
    x = 0
    class Test6Handler(Handler):
        def __call__(self, event: Test6):
            nonlocal x; x = 1
            assert event.__dict__ == {'foo': 'foohere', 'bar': 'barhere'}

    # Event Listener
    # We cannot test string handlers because module.load cannot import from this <locals> location
    uvicore.events.handle('tests.test_events.test6.<locals>.Test6', Test6Handler)

    # Event Dispatcher
    #uvicore.events.dispatch(Test5('foohere', 'barhere'))
    Test6('foohere', 'barhere').dispatch()

    assert x == 1


@pytest.mark.asyncio
async def test1_async(app1):
    """Async - String event, method handler, Dict payload"""

    # Event Handler
    x = 0
    async def handle(event: Dict):
        nonlocal x; x = 1
        assert event == Dict({
            'stuff': 'here',
            'name': 'test1',
            'description': 'String based dynamic event.'
        })

    # Event Listener
    uvicore.events.listen('test1', handle)

    # Event Dispatcher
    await uvicore.events.codispatch('test1', {'stuff': 'here'})

    assert x == 1


@pytest.mark.asyncio
async def test2_async(app1):
    """Async - Class event, method handler, Class payload"""
    from uvicore.events import Event

    # Event
    class Test2(Event):
        def __init__(self, foo, bar):
            self.foo = foo
            self.bar = bar

    # Event Handler
    x = 0
    async def handle(event: Test2):
        nonlocal x; x = 1
        assert event.__dict__ == {'foo': 'foohere', 'bar': 'barhere'}

    # Event Listener
    uvicore.events.listen('tests.test_events.test2_async.<locals>.Test2', handle)

    # Event Dispatcher
    await uvicore.events.codispatch(Test2('foohere', 'barhere'))

    assert x == 1


@pytest.mark.asyncio
async def test3_async(app1):
    """Async - Class event, decorator handler, Class payload"""
    from uvicore.events import Event

    # Event
    class Test3(Event):
        def __init__(self, foo, bar):
            self.foo = foo
            self.bar = bar

    # Event Listener and Handler
    #@uvicore.events.handle('tests.test_events.test3.<locals>.Test3')
    x = 0
    @uvicore.events.handle('tests.test_events.test3_async.<locals>.Test3')
    async def handle(event: Test3):
        nonlocal x; x = 1
        assert event.__dict__ == {'foo': 'foohere', 'bar': 'barhere'}

    # Event Dispatcher
    # await uvicore.events.codispatch(Test3('foohere', 'barhere'))
    await Test3('foohere', 'barhere').codispatch()

    assert x == 1


@pytest.mark.asyncio
async def test4_async(app1):
    """Async - Class event, method handler, Class payload, no strings"""
    from uvicore.events import Event

    # Event
    class Test4(Event):
        def __init__(self, foo, bar):
            self.foo = foo
            self.bar = bar

    # Event Listener and Handler
    x = 0
    async def handle(event: Test4):
        nonlocal x; x = 1
        assert event.__dict__ == {'foo': 'foohere', 'bar': 'barhere'}

    # Event Listener
    # uvicore.events.listen(Test4, handle)
    Test4.listen(handle)

    # Event Dispatcher
    # await uvicore.events.codispatch(Test3('foohere', 'barhere'))
    await Test4('foohere', 'barhere').codispatch()

    assert x == 1


@pytest.mark.asyncio
async def test5_async(app1):
    """Async - Class event, class handler, Class payload, no strings"""
    from uvicore.events import Event, Handler

    # Event
    class Test5(Event):
        def __init__(self, foo, bar):
            self.foo = foo
            self.bar = bar

    # Event Handler
    x = 0
    class Test5Handler(Handler):
        async def __call__(self, event: Test5):
            nonlocal x; x = 1
            assert event.__dict__ == {'foo': 'foohere', 'bar': 'barhere'}

    # Event Listener
    # uvicore.events.listen(Test4, handle)
    Test5.call(Test5Handler)  # .listen, .listener, .handle, .handler, .call are all the same

    # Event Dispatcher
    await uvicore.events.codispatch(Test5('foohere', 'barhere'))

    assert x == 1


@pytest.mark.asyncio
async def test6_async(app1):
    """Async - Class event, class handler, Class payload"""
    from uvicore.events import Event, Handler

    # Event
    class Test6(Event):
        def __init__(self, foo, bar):
            self.foo = foo
            self.bar = bar

    # Event Handler
    x = 0
    class Test6Handler(Handler):
        async def __call__(self, event: Test6):
            nonlocal x; x = 1
            assert event.__dict__ == {'foo': 'foohere', 'bar': 'barhere'}

    # Event Listener
    # We cannot test string handlers because module.load cannot import from this <locals> location
    uvicore.events.handle('tests.test_events.test6_async.<locals>.Test6', Test6Handler)

    # Event Dispatcher
    # await uvicore.events.codispatch(Test5('foohere', 'barhere'))
    await Test6('foohere', 'barhere').codispatch()

    assert x == 1

