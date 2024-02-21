import pytest
import uvicore
from uvicore.support.dumper import dump

# DB ORM

@pytest.mark.asyncio
async def test_single(app1):
    # Single NOT where like
    from app1.models.post import Post
    query = Post.query().where('body', '!like', '%favorite%')
    # Probably not as this could be dialect specific
    #assert query.sql() == {'main': 'SELECT DISTINCT posts.id, posts.unique_slug, posts.title, posts.body, posts.other, posts.creator_id, posts.owner_id FROM posts WHERE posts.body NOT LIKE :body_1'}
    posts = await query.order_by('id').get()
    assert [1, 3, 5, 6, 7] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_and(app1):
    # Multiple NOT where like AND
    from app1.models.post import Post
    posts = await Post.query().where('body', '!like', '%favorite%').where('body', '!like', '%i lik%').order_by('id').get()
    assert [5, 6] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_and_list(app1):
    # Multiple NOT where like AND using a LIST
    from app1.models.post import Post
    posts = await Post.query().where([
        ('body', '!like', '%favorite%'),
        ('body', '!like', '%i lik%')
    ]).order_by('id').get()
    assert [5, 6] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_or(app1):
    # Where NOT like OR
    from app1.models.post import Post
    posts = await Post.query().or_where([
        ('body', '!like', '%I like%'),
        ('slug', '=', 'test-post1'),
    ]).order_by('id').get()
    assert [1, 2, 4, 5, 6] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_and_or(app1):
    # Where NOT like AND with where OR
    from app1.models.post import Post
    posts = await Post.query().where('body', '!like', '%like%').or_where([
        ('slug', 'test-post3'),
        ('slug', '=', 'test-post6'),
        ('slug', '=', 'test-post5'),
    ]).order_by('id').get()
    assert [5, 6] == [x.id for x in posts]
