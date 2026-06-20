import pytest
import uvicore
from uvicore.support.dumper import dump


@pytest.mark.asyncio
async def test_user_model_exists(app1):
    """Test that User model exists and is accessible"""
    from uvicore.auth.models.user import User
    assert User is not None, "User model should exist"


@pytest.mark.asyncio
async def test_user_query_get(app1):
    """Test querying users"""
    from uvicore.auth.models.user import User
    users = await User.query().get()
    assert isinstance(users, list)
    assert len(users) > 0


@pytest.mark.asyncio
async def test_user_find_by_id(app1):
    """Test finding user by ID"""
    from uvicore.auth.models.user import User
    user = await User.query().find(1)
    assert user is not None
    assert user.id == 1


@pytest.mark.asyncio
async def test_user_model_has_attributes(app1):
    """Test User model attributes"""
    from uvicore.auth.models.user import User
    user = await User.query().find(1)
    assert user is not None
    # User should have common attributes
    assert hasattr(user, 'id')
    assert hasattr(user, 'email')
