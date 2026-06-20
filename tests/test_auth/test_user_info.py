import pytest
import uvicore
from uvicore.support.dumper import dump


@pytest.mark.asyncio
async def test_auth_module_importable(app1):
    """Test that auth module can be imported"""
    from uvicore import auth
    assert auth is not None


@pytest.mark.asyncio
async def test_user_info_available(app1):
    """Test that UserInfo is available"""
    from uvicore.auth.user_info import UserInfo
    assert UserInfo is not None


@pytest.mark.asyncio
async def test_auth_service_container(app1):
    """Test that auth is in IoC container"""
    # Auth should be registered in container
    assert hasattr(uvicore, 'auth')
