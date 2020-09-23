import pytest
import uvicore
from typing import List
from uvicore.support.dumper import dump
from starlette.testclient import TestClient

# Typechecking imports only
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app1.models.user import UserModel
    from app1.models.post import PostModel


@pytest.mark.asyncio
async def test_where_equal(bootstrap_app1):
    # Test Ioc instead of import
    User: UserModel = uvicore.ioc.make('uvicore.auth.models.user.User')

    # Test implicit =
    users: List[UserModel] = await User.where('email', 'manager1@example.com').get()
    assert ['manager1@example.com'] == [x.email for x in users]

    # Test explicit =
    users: List[UserModel] = await User.where('email', '=', 'manager1@example.com').get()
    assert ['manager1@example.com'] == [x.email for x in users]


@pytest.mark.asyncio
async def test_where_notequal(bootstrap_app1):
    from uvicore.auth.models.user import User

    # Single where
    users: List[UserModel] = await User.where('email', '!=', 'manager1@example.com').get()
    assert [
        'administrator@example.com',
        'manager2@example.com',
        'user1@example.com',
        'user2@example.com',
    ] == [x.email for x in users]

    # Double where
    users: List[UserModel] = await (User
        .where('email', '!=', 'manager1@example.com')
        .where('email', '!=', 'manager2@example.com')
        .get()
    )
    assert [
        'administrator@example.com',
        'user1@example.com',
        'user2@example.com',
    ] == [x.email for x in users]


@pytest.mark.asyncio
async def test_where_in(bootstrap_app1):
    from uvicore.auth.models.user import User

    users: List[UserModel] = await (User
        .where('email', 'in', [
            'manager1@example.com',
            'manager2@example.com',
        ])
        .get()
    )
    assert [
        'manager1@example.com',
        'manager2@example.com',
    ] == [x.email for x in users]


@pytest.mark.asyncio
async def test_where_not_in(bootstrap_app1):
    from uvicore.auth.models.user import User

    users: List[UserModel] = await (User
        .where('email', '!in', [
            'manager1@example.com',
            'manager2@example.com',
        ])
        .get()
    )
    assert [
        'administrator@example.com',
        'user1@example.com',
        'user2@example.com',
    ] == [x.email for x in users]


@pytest.mark.asyncio
async def test_where_like(bootstrap_app1):
    from uvicore.auth.models.user import User

    users: List[UserModel] = await(User
        .where('email', 'like', 'manager%')
        .get()
    )
    assert [
        'manager1@example.com',
        'manager2@example.com',
    ] == [x.email for x in users]


@pytest.mark.asyncio
async def test_where_not_like(bootstrap_app1):
    from uvicore.auth.models.user import User
    users: List[UserModel] = await(User
        .where('email', '!like', 'manager%')
        .get()
    )
    assert [
        'administrator@example.com',
        'user1@example.com',
        'user2@example.com',
    ] == [x.email for x in users]


@pytest.mark.asyncio
async def test_where_null(bootstrap_app1):
    from app1.models.post import Post

    # Implicit =
    posts: List[PostModel] = await Post.where('other', 'null').get()
    dump(posts)
    assert [
        'test-post2',
        'test-post4',
        'test-post5',
        'test-post7',
    ] == [x.slug for x in posts]

    # Explicit =
    posts: List[PostModel] = await Post.where('other', '=', 'null').get()
    dump(posts)
    assert [
        'test-post2',
        'test-post4',
        'test-post5',
        'test-post7',
    ]== [x.slug for x in posts]

    # Where not NULL
    posts: List[PostModel] = await Post.where('other', '!=', 'null').get()
    dump(posts)
    assert [
        'test-post1',
        'test-post3',
        'test-post6',
    ] == [x.slug for x in posts]


@pytest.mark.asyncio
async def test_where_or(bootstrap_app1):
    from uvicore.auth.models.user import User
    users: List[UserModel] = await (User
        .or_where([
            ('email', 'manager1@example.com'),
            ('email', 'manager2@example.com'),
        ])
        .get()
    )
    assert [
        'manager1@example.com',
        'manager2@example.com',
    ] == [x.email for x in users]


@pytest.mark.asyncio
async def test_where_or_in(bootstrap_app1):
    from uvicore.auth.models.user import User
    users: List[UserModel] = await (User
        .or_where([
            ('email', 'in', ['manager1@example.com', 'manager2@example.com']),
            ('id', 'in', [1,4]),
        ])
        .get()
    )
    assert [
        'administrator@example.com',
        'manager1@example.com',
        'manager2@example.com',
        'user1@example.com',
    ] == [x.email for x in users]


@pytest.mark.asyncio
async def test_where_or_not_in(bootstrap_app1):
    from uvicore.auth.models.user import User
    users: List[UserModel] = await (User
        .or_where([
            ('email', '!in', ['manager1@example.com', 'manager2@example.com']),
            ('id', 2),
        ])
        .get()
    )
    assert [
        'administrator@example.com',
        'manager1@example.com',
        'user1@example.com',
        'user2@example.com',
    ] == [x.email for x in users]


@pytest.mark.asyncio
async def test_where_or_like(bootstrap_app1):
    from uvicore.auth.models.user import User
    users: List[UserModel] = await (User
        .or_where([
            ('email', 'like', 'manager%'),
            ('email', 'like', 'user%'),
        ])
        .get()
    )
    assert [
        'manager1@example.com',
        'manager2@example.com',
        'user1@example.com',
        'user2@example.com',
    ] == [x.email for x in users]


@pytest.mark.asyncio
async def test_where_or_not_like(bootstrap_app1):
    from uvicore.auth.models.user import User
    users: List[UserModel] = await (User
        .or_where([
            ('email', '!like', 'manager%'),
            ('id', 2),
        ])
        .get()
    )
    assert [
        'administrator@example.com',
        'manager1@example.com',
        'user1@example.com',
        'user2@example.com',
    ] == [x.email for x in users]

