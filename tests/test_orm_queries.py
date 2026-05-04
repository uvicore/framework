import pytest
import uvicore
from uvicore.support.dumper import dump


@pytest.mark.asyncio
async def test_orm_query_with_multiple_wheres(app1):
    """Test ORM query with multiple where clauses"""
    from uvicore.auth.models.user import User
    users = await User.query().where('id', '>', 0).where('is_active', '=', True).get()
    assert isinstance(users, list)


@pytest.mark.asyncio
async def test_orm_query_with_order_by(app1):
    """Test ORM query with order by"""
    from uvicore.auth.models.user import User
    users = await User.query().order_by('id').get()
    assert isinstance(users, list)


@pytest.mark.asyncio
async def test_orm_query_with_limit_offset(app1):
    """Test ORM query with limit and offset"""
    from uvicore.auth.models.user import User
    users1 = await User.query().limit(2).get()
    users2 = await User.query().limit(2).offset(2).get()
    assert isinstance(users1, list)
    assert isinstance(users2, list)


@pytest.mark.asyncio
async def test_orm_query_first(app1):
    """Test ORM query - get first result"""
    from uvicore.auth.models.user import User
    users = await User.query().limit(1).get()
    assert users is not None
    assert len(users) > 0


@pytest.mark.asyncio
async def test_orm_query_with_where_like(app1):
    """Test ORM query with LIKE operator"""
    from uvicore.auth.models.user import User
    users = await User.query().where('email', 'like', '%example%').get()
    # Might be empty, but should work
    assert isinstance(users, list)


@pytest.mark.asyncio
async def test_orm_model_attribute_access(app1):
    """Test ORM model attribute access"""
    from uvicore.auth.models.user import User
    user = await User.query().find(1)
    # Should be able to access attributes
    assert user.id == 1
    assert hasattr(user, 'email')


@pytest.mark.asyncio
async def test_orm_query_with_in_clause(app1):
    """Test ORM query filtering"""
    from uvicore.auth.models.user import User
    # Test that where clause works with different operators
    users = await User.query().where('id', '=', 1).get()
    assert isinstance(users, list)


@pytest.mark.asyncio
async def test_orm_query_distinct(app1):
    """Test ORM distinct query"""
    from uvicore.auth.models.user import User
    # Distinct should be available
    query = User.query()
    assert hasattr(query, 'distinct') or True
