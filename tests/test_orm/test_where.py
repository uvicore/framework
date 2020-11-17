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
async def test_where_in(app1):
    from uvicore.auth.models.user import User

    users: List[UserModel] = await (User.query()
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
async def test_where_not_in(app1):
    from uvicore.auth.models.user import User

    users: List[UserModel] = await (User.query()
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
async def test_where_like(app1):
    from uvicore.auth.models.user import User

    users: List[UserModel] = await(User.query()
        .where('email', 'like', 'manager%')
        .get()
    )
    assert [
        'manager1@example.com',
        'manager2@example.com',
    ] == [x.email for x in users]


@pytest.mark.asyncio
async def test_where_not_like(app1):
    from uvicore.auth.models.user import User
    users: List[UserModel] = await(User.query()
        .where('email', '!like', 'manager%')
        .get()
    )
    assert [
        'administrator@example.com',
        'user1@example.com',
        'user2@example.com',
    ] == [x.email for x in users]


@pytest.mark.asyncio
async def test_where_null(app1):
    from app1.models.post import Post

    # Implicit =
    posts: List[PostModel] = await Post.query().where('other', 'null').get()
    dump(posts)
    assert [
        'test-post2',
        'test-post4',
        'test-post5',
        'test-post7',
    ] == [x.slug for x in posts]

    # Explicit =
    posts: List[PostModel] = await Post.query().where('other', '=', 'null').get()
    dump(posts)
    assert [
        'test-post2',
        'test-post4',
        'test-post5',
        'test-post7',
    ]== [x.slug for x in posts]

    # Where not NULL
    posts: List[PostModel] = await Post.query().where('other', '!=', 'null').get()
    dump(posts)
    assert [
        'test-post1',
        'test-post3',
        'test-post6',
    ] == [x.slug for x in posts]


@pytest.mark.asyncio
async def test_where_or(app1):
    from uvicore.auth.models.user import User
    users: List[UserModel] = await (User.query()
        .or_where([
            ('email', 'manager1@example.com'),
            ('email', 'manager2@example.com'),
        ])
        .get()
    )
    dump(users)
    assert [
        'manager1@example.com',
        'manager2@example.com',
    ] == [x.email for x in users]


@pytest.mark.asyncio
async def test_where_and_or(app1):
    from uvicore.auth.models.user import User
    users: List[UserModel] = await (User.query()
        .where('app1_extra', None)
        .or_where([
            ('email', 'manager1@example.com'),
            ('email', 'user2@example.com'),
        ])
        .get()
    )
    dump(users)
    assert [
        'manager1@example.com',
        'user2@example.com',
    ] == [x.email for x in users]


@pytest.mark.asyncio
async def test_where_or_in(app1):
    from uvicore.auth.models.user import User
    users: List[UserModel] = await (User.query()
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
async def test_where_or_not_in(app1):
    from uvicore.auth.models.user import User
    users: List[UserModel] = await (User.query()
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
async def test_where_or_like(app1):
    from uvicore.auth.models.user import User
    users: List[UserModel] = await (User.query()
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
async def test_where_or_not_like(app1):
    from uvicore.auth.models.user import User
    users: List[UserModel] = await (User.query()
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


