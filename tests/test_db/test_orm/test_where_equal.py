import pytest
import uvicore
from uvicore.support.dumper import dump

# DB ORM

@pytest.mark.asyncio
async def test_single(app1):
    # Single where
    from app1.models.post import Post
    posts = await Post.query().where('creator_id', 2).get()
    assert [3, 4, 5] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_and(app1):
    # Multiple where AND
    from app1.models.post import Post
    posts = await Post.query().where('creator_id', '=', 2).where('owner_id', 1).get()
    assert [3, 4] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_and_list(app1):
    # Multiple where AND using a LIST
    from app1.models.post import Post
    posts = await Post.query().where([
        ('creator_id', '=', 2),
        ('owner_id', 1)
    ]).get()
    assert [3, 4] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_or(app1):
    # Where OR
    from app1.models.post import Post
    posts = await Post.query().or_where([
        ('slug', 'test-post3'),
        ('slug', '=', 'test-post4'),
    ]).get()
    assert [3, 4] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_and_or(app1):
    # Where AND with where OR
    from app1.models.post import Post
    posts = await Post.query().where('creator_id', '=', 2).or_where([
        ('slug', 'test-post3'),
        ('slug', '=', 'test-post4'),
    ]).get()
    assert [3, 4] == [x.id for x in posts]
