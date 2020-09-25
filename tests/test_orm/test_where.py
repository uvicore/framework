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
    #User = uvicore.ioc.make('uvicore.auth.models.user.User')
    from uvicore.auth.models.user import User

    # Test implicit =
    users: List[UserModel] = await User.where('email', 'manager1@example.com').get()
    dump(users)
    assert ['manager1@example.com'] == [x.email for x in users]

    # Test explicit =
    users: List[UserModel] = await User.where('email', '=', 'manager1@example.com').get()
    dump(users)
    assert ['manager1@example.com'] == [x.email for x in users]


@pytest.mark.asyncio
async def test_where_column_mapper(bootstrap_app1):
    from app1.models.post import Post

    # The model field `slug` is table column `unique_slug`
    # So we are testing that we can where on `slug` and it translate to table `unique_slug`
    posts = await Post.query().where('slug', 'test-post3').get()
    dump(posts)
    assert ['Test Post3'] == [x.title for x in posts]


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
async def test_where_and_or(bootstrap_app1):
    from uvicore.auth.models.user import User
    users: List[UserModel] = await (User
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


@pytest.mark.asyncio
async def test_where_relation(bootstrap_app1):
    from uvicore.auth.models.user import User
    from app1.models.post import Post

    # Test relation where
    users = await User.query().include('contact').where('contact.phone', '111-111-1111').get()
    dump(users)
    assert ['Manager1'] == [x.contact.title for x in users]

    # Test muli-level where
    posts = await Post.query().include('creator.contact').where('creator.contact.name', 'Manager One').get()
    dump(posts)
    assert [
        'test-post3',
        'test-post4',
        'test-post5',
    ] == [x.slug for x in posts]

    # Test muli-level where
    # Slug is also a column mapper, database colun is called `unique_slug`, we get that test too!
    posts = (await Post.query()
        .include('creator.contact')
        .where('creator.contact.name', 'Manager One')
        .or_where([
            ('slug', 'test-post3'),
            ('slug', 'test-post5')
        ])
        .get()
    )
    dump(posts)
    assert [
        'test-post3',
        'test-post5',
    ] == [x.slug for x in posts]
