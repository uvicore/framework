import pytest
import uvicore
from uvicore.support.dumper import dump


@pytest.mark.asyncio
async def test_cache_service_available(app1):
    """Test that cache service is available"""
    assert hasattr(uvicore, 'cache'), "Cache service should be available"


@pytest.mark.asyncio
async def test_cache_get_method(app1):
    """Test cache.get() method"""
    cache = uvicore.cache
    assert hasattr(cache, 'get'), "Cache should have get method"


@pytest.mark.asyncio
async def test_cache_put_method(app1):
    """Test cache.put() method"""
    cache = uvicore.cache
    assert hasattr(cache, 'put'), "Cache should have put method"


@pytest.mark.asyncio
async def test_cache_forget_method(app1):
    """Test cache.forget() method"""
    cache = uvicore.cache
    assert hasattr(cache, 'forget'), "Cache should have forget method"


@pytest.mark.asyncio
async def test_cache_store_method(app1):
    """Test cache.store() method"""
    cache = uvicore.cache
    assert hasattr(cache, 'store'), "Cache should have store method"


@pytest.mark.asyncio
async def test_cache_put_and_get(app1):
    """Test cache put and get operations"""
    cache = uvicore.cache
    key = 'test-cache-key'
    value = 'test-value'

    # Put value in cache
    await cache.put(key, value, seconds=3600)

    # Get value from cache
    cached_value = await cache.get(key)
    assert cached_value == value


@pytest.mark.asyncio
async def test_cache_forget_operation(app1):
    """Test cache forget operation"""
    cache = uvicore.cache
    key = 'test-forget-key'

    # Put value in cache
    await cache.put(key, 'test', seconds=3600)

    # Forget it
    await cache.forget(key)

    # Should be gone
    result = await cache.get(key)
    assert result is None
