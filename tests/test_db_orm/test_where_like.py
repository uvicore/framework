import pytest
import uvicore
from uvicore.support.dumper import dump

# DB ORM

@pytest.mark.asyncio
async def test_single(app1):
    # Single where like
    from app1.models.post import Post
    query = Post.query().where('body', 'like', '%favorite%')
    # Probably not as this could be dialect specific
    #assert query.sql() == {'main': 'SELECT DISTINCT posts.id, posts.unique_slug, posts.title, posts.body, posts.other, posts.creator_id, posts.owner_id FROM posts WHERE posts.body LIKE :body_1'}
    posts = await query.get()
    assert [2, 4] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_and(app1):
    # Multiple where like AND
    from app1.models.post import Post
    posts = await Post.query().where('body', 'like', '%favorite%').where('body', 'like', '%frameworks%').get()
    assert [2] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_and_list(app1):
    # Multiple where like AND using a LIST
    from app1.models.post import Post
    posts = await Post.query().where([
        ('body', 'like', '%favorite%'),
        ('body', 'like', '%frameworks%')
    ]).get()
    assert [2] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_or(app1):
    # Where like OR
    from app1.models.post import Post
    posts = await Post.query().or_where([
        ('body', 'like', '%favorite%'),
        ('body', 'like', '%love%'),
    ]).get()
    assert [2, 4, 5] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_and_or(app1):
    # Where like AND with where OR
    from app1.models.post import Post
    posts = await Post.query().where('body', 'like', '%like%').or_where([
        ('slug', 'test-post3'),
        ('slug', '=', 'test-post6'),
        ('slug', '=', 'test-post7'),
    ]).get()
    assert [3, 7] == [x.id for x in posts]
