import pytest
import uvicore
from uvicore.support.dumper import dump


@pytest.mark.asyncio
async def test_middleware_module_exists(app1):
    """Test middleware module"""
    from uvicore.http import middleware
    assert middleware is not None


@pytest.mark.asyncio
async def test_guard_class_importable(app1):
    """Test Guard class"""
    from uvicore.http.routing import Guard
    guard = Guard()
    assert guard is not None


@pytest.mark.asyncio
async def test_guard_with_scopes(app1):
    """Test Guard with authorization scopes"""
    from uvicore.http.routing import Guard
    guard = Guard(['admin', 'moderator'])
    assert guard is not None
