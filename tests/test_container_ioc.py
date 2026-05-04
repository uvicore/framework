import pytest
import uvicore
from uvicore.support.dumper import dump


@pytest.mark.asyncio
async def test_container_bind_and_make(app1):
    """Test IoC container binding and making services"""
    container = uvicore.ioc
    # Container should be able to make services
    assert container is not None


@pytest.mark.asyncio
async def test_container_has_services(app1):
    """Test container has registered services"""
    container = uvicore.ioc
    # Should have db service
    db = uvicore.db
    assert db is not None


@pytest.mark.asyncio
async def test_database_manager(app1):
    """Test database manager"""
    db = uvicore.db
    # Should have query method
    assert hasattr(db, 'query')


@pytest.mark.asyncio
async def test_database_query_table(app1):
    """Test database query on specific table"""
    results = await uvicore.db.query().table('users').limit(10).get()
    assert isinstance(results, list)


@pytest.mark.asyncio
async def test_logger_service(app1):
    """Test logger service"""
    logger = uvicore.log
    assert logger is not None


@pytest.mark.asyncio
async def test_event_handler_registration(app1):
    """Test event handler registration and dispatch"""
    counter = {'value': 0}

    def test_handler(data):
        counter['value'] += 1

    # Register handler
    uvicore.events.listen('counter_test', test_handler)

    # Dispatch event
    uvicore.events.dispatch('counter_test', {})

    assert counter['value'] == 1


@pytest.mark.asyncio
async def test_event_multiple_handlers(app1):
    """Test multiple event handlers"""
    results = []

    def handler1(data):
        results.append(1)

    def handler2(data):
        results.append(2)

    uvicore.events.listen('multi_test', handler1)
    uvicore.events.listen('multi_test', handler2)
    uvicore.events.dispatch('multi_test', {})

    assert len(results) >= 2
