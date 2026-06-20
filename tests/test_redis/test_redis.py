import pytest
import uvicore
from uvicore.support.dumper import dump


@pytest.mark.asyncio
async def test_redis_service_available(app1):
    """Test that redis service is available"""
    # Redis may not be configured in test config, so we just check if available
    assert hasattr(uvicore, 'redis'), "Redis service should be available"


@pytest.mark.asyncio
async def test_redis_module_importable(app1):
    """Test that redis module can be imported"""
    from uvicore import redis
    assert redis is not None


@pytest.mark.asyncio
async def test_redis_connection_method_exists(app1):
    """Test that Redis has connection management"""
    from uvicore.redis import Redis
    assert hasattr(Redis, 'connection'), "Redis should have connection method"
