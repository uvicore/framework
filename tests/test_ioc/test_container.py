"""
Core IoC container behavior: make() by name and alias, binding lookup, singleton
vs non-singleton resolution, default fallback, and clear errors.

Consolidated + strengthened from the former shallow tests/test_container_ioc.py
(which only asserted `container is not None`). The override/_BASE mechanism is
covered by the sibling test_overrides.py; the event system by tests/test_events.py.
"""
import pytest
import uvicore


@pytest.mark.asyncio
async def test_make_by_name_and_alias_returns_same_singleton(app1):
    """A singleton service resolves to one instance via full name or any alias."""
    by_name = uvicore.ioc.make('uvicore.database.db.Db')
    by_alias1 = uvicore.ioc.make('Database')
    by_alias2 = uvicore.ioc.make('db')
    assert by_name is by_alias1 is by_alias2 is uvicore.db


@pytest.mark.asyncio
async def test_binding_lookup(app1):
    """binding() returns the Binding metadata for a name or alias."""
    binding = uvicore.ioc.binding('Database')
    assert binding is not None
    assert binding.singleton is True


@pytest.mark.asyncio
async def test_bind_and_make_non_singleton(app1):
    """A non-singleton class bind (no kwargs/factory) resolves to the class itself."""
    class WidgetService:
        def greet(self):
            return 'hi'
    uvicore.ioc.bind('tests.WidgetService', WidgetService, aliases=['WidgetService'])
    made = uvicore.ioc.make('WidgetService')
    assert made is WidgetService
    assert made().greet() == 'hi'


@pytest.mark.asyncio
async def test_bind_and_make_singleton(app1):
    """A singleton bind resolves to the same instance every time."""
    class CounterService:
        pass
    uvicore.ioc.bind('tests.CounterService', CounterService, singleton=True)
    a = uvicore.ioc.make('tests.CounterService')
    b = uvicore.ioc.make('tests.CounterService')
    assert a is b
    assert isinstance(a, CounterService)


@pytest.mark.asyncio
async def test_make_with_default_binds_fallback(app1):
    """make(name, default) binds and returns the default when no binding exists yet."""
    class DefaultService:
        pass
    made = uvicore.ioc.make('tests.DefaultService', DefaultService)
    assert made is DefaultService
    # Now bound, a second make resolves the same binding
    assert uvicore.ioc.make('tests.DefaultService') is DefaultService


@pytest.mark.asyncio
async def test_make_unknown_name_raises(app1):
    """An unknown (dot-less) IoC name raises a clear ModuleNotFoundError."""
    with pytest.raises(ModuleNotFoundError):
        uvicore.ioc.make('NoSuchServiceXyz')


@pytest.mark.asyncio
async def test_db_service_from_ioc_is_functional(app1):
    """The db service resolved from the container actually executes queries."""
    db = uvicore.ioc.make('db')
    rows = await db.query('app1').table('posts').limit(3).get()
    assert len(rows) == 3
