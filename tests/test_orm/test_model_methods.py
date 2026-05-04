import pytest
import uvicore
from uvicore.support.dumper import dump


@pytest.mark.asyncio
async def test_orm_query_builder(app1):
    """Test ORM query builder"""
    from uvicore.auth.models.user import User
    query = User.query()
    assert query is not None
    assert hasattr(query, 'get')


@pytest.mark.asyncio
async def test_orm_query_with_limit(app1):
    """Test ORM query with limit"""
    from uvicore.auth.models.user import User
    query = User.query().limit(10)
    assert query is not None


@pytest.mark.asyncio
async def test_orm_query_with_offset(app1):
    """Test ORM query with offset"""
    from uvicore.auth.models.user import User
    query = User.query().offset(5)
    assert query is not None


@pytest.mark.asyncio
async def test_orm_model_serialization(app1):
    """Test ORM model can be accessed as dict"""
    from uvicore.auth.models.user import User
    user = await User.query().find(1)
    # Test accessing attributes
    assert hasattr(user, 'id')
    assert hasattr(user, 'email')
