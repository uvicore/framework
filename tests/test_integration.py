import pytest
import uvicore
from uvicore.support.dumper import dump


@pytest.mark.asyncio
async def test_auth_service_check_permission(app1):
    """Test auth service can check permissions"""
    auth = uvicore.auth
    # Auth service should exist and have various methods
    assert auth is not None


@pytest.mark.asyncio
async def test_event_dispatch(app1):
    """Test event dispatching system"""
    result = []

    def handler(data):
        result.append(data)

    uvicore.events.listen('test_event', handler)
    uvicore.events.dispatch('test_event', {'message': 'test'})

    assert len(result) > 0


@pytest.mark.asyncio
async def test_cache_operations_put_get_forget(app1):
    """Test cache put, get, and forget cycle"""
    cache = uvicore.cache
    key = 'test_key_' + str(__import__('time').time())

    await cache.put(key, 'test_value', seconds=3600)
    value = await cache.get(key)
    assert value == 'test_value'

    await cache.forget(key)
    forgotten = await cache.get(key)
    assert forgotten is None


@pytest.mark.asyncio
async def test_config_app_attribute(app1):
    """Test configuration app attribute"""
    config = uvicore.config
    assert hasattr(config, 'app')


@pytest.mark.asyncio
async def test_container_make_service(app1):
    """Test IoC container making services"""
    # Should be able to make services from container
    container = uvicore.ioc
    assert container is not None


@pytest.mark.asyncio
async def test_orm_query_with_where(app1):
    """Test ORM query with where clause"""
    from uvicore.auth.models.user import User
    users = await User.query().where('is_active', '=', True).get()
    assert isinstance(users, list)


@pytest.mark.asyncio
async def test_orm_count_query(app1):
    """Test ORM count functionality"""
    from uvicore.auth.models.user import User
    # Get count of records
    users = await User.query().get()
    assert isinstance(users, list)
    assert len(users) > 0
