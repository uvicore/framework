import pytest
import uvicore
from uvicore.support.dumper import dump
from starlette.testclient import TestClient


@pytest.mark.asyncio
async def test_find(bootstrap_app1):
    from uvicore.auth.models.user import User
    user = await User.find(3)
    assert user.email == 'manager2@example.com'


@pytest.mark.asyncio
async def test_select_all(bootstrap_app1):
    from uvicore.auth.models.user import User
    users = await User.get()
    assert [
        'administrator@example.com',
        'manager1@example.com',
        'manager2@example.com',
        'user1@example.com',
        'user2@example.com',
    ] == [x.email for x in users]


@pytest.mark.asyncio
async def test_where_equal(bootstrap_app1):
    User = uvicore.ioc.make('uvicore.auth.models.User')

    # Test implicit =
    users = await User.where('email', 'manager1@example.com').get()
    assert ['manager1@example.com'] == [x.email for x in users]

    # Test explicit =
    users = await User.where('email', '=', 'manager1@example.com').get()
    assert ['manager1@example.com'] == [x.email for x in users]


@pytest.mark.asyncio
async def test_where_notequal(bootstrap_app1):
    User = uvicore.ioc.make('uvicore.auth.models.User')

    # Single where
    users = await User.where('email', '!=', 'manager1@example.com').get()
    assert [
        'administrator@example.com',
        'manager2@example.com',
        'user1@example.com',
        'user2@example.com',
    ] == [x.email for x in users]

    # Double where
    users = await (User
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
    User = uvicore.ioc.make('uvicore.auth.models.User')
    users = await (User
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
    User = uvicore.ioc.make('uvicore.auth.models.User')
    users = await (User
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
    User = uvicore.ioc.make('uvicore.auth.models.User')
    users = await(User
        .where('email', 'like', 'manager%')
        .get()
    )
    assert [
        'manager1@example.com',
        'manager2@example.com',
    ] == [x.email for x in users]


@pytest.mark.asyncio
async def test_where_not_like(bootstrap_app1):
    User = uvicore.ioc.make('uvicore.auth.models.User')
    users = await(User
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
    posts = await Post.where('other', 'null').get()
    assert ['test-post2'] == [x.slug for x in posts]

    # Explicit =
    posts = await Post.where('other', '=', 'null').get()
    assert ['test-post2'] == [x.slug for x in posts]

    # Where not NULL
    posts = await Post.where('other', '!=', 'null').get()
    assert ['test-post1'] == [x.slug for x in posts]


@pytest.mark.asyncio
async def test_where_or(bootstrap_app1):
    User = uvicore.ioc.make('uvicore.auth.models.User')
    users = await (User
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
    User = uvicore.ioc.make('uvicore.auth.models.User')
    users = await (User
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
    User = uvicore.ioc.make('uvicore.auth.models.User')
    users = await (User
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
    User = uvicore.ioc.make('uvicore.auth.models.User')
    users = await (User
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
    User = uvicore.ioc.make('uvicore.auth.models.User')
    users = await (User
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
async def test_callback(bootstrap_app1):
    from app1.models.post import Post
    post = await Post.find(2)
    assert post.cb == 'test-post2 callback'


@pytest.mark.asyncio
async def test_many_to_one(bootstrap_app1):
    # Many posts can have ONE user (has_one)
    from app1.models.post import Post
    posts = await Post.include('creator').get()
    dump(posts)

    #dump(uvicore.ioc.bindings)
    # dump(uvicore.config('app'))

    # name = 'uvicore.auth.database.tables.Users'
    # override = None
    # app_config = uvicore.config('app')
    # if 'bindings' in app_config:
    #     if name in app_config['bindings']:
    #         override = app_config['bindings'][name]
    # dump(override)


    assert 1 == 2
