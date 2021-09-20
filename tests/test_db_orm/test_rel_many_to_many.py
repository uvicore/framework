import pytest
import uvicore
from uvicore.support.dumper import dump, dd


@pytest.mark.asyncio
async def test_select_one(app1):
    from app1.models.post import Post
    post = await Post.query().include('tags').find(1)
    dump(post)
    assert post.slug == 'test-post1'
    assert [
        'linux',
        'mac',
        'bsd',
        'test1',
        'test2'
    ] == [x.name for x in post.tags]


@pytest.mark.asyncio
async def test_select_many(app1):
    from app1.models.post import Post
    posts = await Post.query().include('tags').get()
    dump(posts)
    assert len(posts) == 7
    assert [
        'linux',
        'mac',
        'bsd',
        'test1',
        'test2'
    ] == [x.name for x in posts[0].tags]
    assert [
        'linux',
        'bsd',
    ] == [x.name for x in posts[1].tags]
    assert [
        'linux',
        'bsd',
        'laravel'
    ] == [x.name for x in posts[6].tags]


@pytest.mark.asyncio
async def test_where(app1):
    from app1.models.post import Post

    # Remember these children level wheres only filter the parent (posts)
    # but all tags for those parents are still shown.  Use .filter() to filter children.
    posts = await Post.query().include('tags').where('tags.name', 'linux').get()
    dump(posts)

    # Should filter parent
    assert [
        'test-post1',
        'test-post2',
        'test-post7',
    ] == [x.slug for x in posts]

    # But not any children
    assert len(posts[0].tags) == 5
    assert len(posts[1].tags) == 2
    assert len(posts[2].tags) == 3


@pytest.mark.asyncio
async def test_where_through_one_to_many(app1):
    #from uvicore.auth.models.user import User
    from app1.models.user import User

    users = await User.query().include(
        'posts',  # The One-To-Many the Many-To-Many is going through
        'posts.tags',  # Many-To-Many
    ).where('posts.tags.name', 'linux').get()
    dump(users)

    # Should limit by just 2 users
    assert [
        'anonymous@example.com',
        'user1@example.com',
    ] == [x.email for x in users]

    # But should not filter any children
    assert len(users[0].posts) == 2
    assert len(users[1].posts) == 1
    assert len(users[0].posts[0].tags) == 5
    assert len(users[0].posts[1].tags) == 2
    assert len(users[1].posts[0].tags) == 3


@pytest.mark.asyncio
async def test_filter(app1):
    from app1.models.post import Post

    # Filters limit the children records only, never parents.
    # So this still shows ALL posts, but for each post, only shows tags that = linux
    posts = await Post.query().include('tags').filter('tags.name', 'linux').get()
    dump(posts)
    assert len(posts) == 7
    assert len(posts[0].tags) == 1
    assert len(posts[1].tags) == 1
    assert len(posts[6].tags) == 1


@pytest.mark.asyncio
async def test_or_filter(app1):
    from app1.models.post import Post

    # Filters limit the children records only, never parents.
    # So this still shows ALL posts, but for each post, only shows tags that = linux OR mac
    posts = await Post.query().include('tags').or_filter([
        ('tags.name', 'linux'),
        ('tags.name', 'mac'),
    ]).get()
    dump(posts)
    assert len(posts) == 7
    assert len(posts[0].tags) == 2
    assert len(posts[1].tags) == 1
    assert len(posts[6].tags) == 1
