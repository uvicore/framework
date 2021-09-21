import pytest
import uvicore
from uvicore.support.dumper import dump

# DB ORM

@pytest.mark.asyncio
async def test_single(app1):
    # Single where NOT
    from app1.models.post import Post
    posts = await Post.query().where('creator_id', '!=', 2).get()
    assert [1, 2, 6, 7] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_and(app1):
    # Multiple where NOT AND
    from app1.models.post import Post
    posts = await Post.query().where('creator_id', '!=', 2).where('owner_id', '!=', 2).get()
    assert [6, 7] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_and_list(app1):
    # Multiple where NOT AND using a LIST
    from app1.models.post import Post
    posts = await Post.query().where([
        ('creator_id', '!=', 2),
        ('owner_id', '!=', 2),
    ]).get()
    assert [6, 7] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_or(app1):
    # Where NOT OR
    from app1.models.post import Post
    posts = await Post.query().or_where([
        ('creator_id', '!=', 1),
        ('owner_id', '!=', 2)
    ]).get()
    assert [3, 4, 5, 6, 7] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_and_or(app1):
    # Where NOT AND with where OR
    from app1.models.post import Post
    posts = await Post.query().where('unique_slug', '!=', 'test-post5').or_where([
        ('creator_id', '!=', 1),
        ('owner_id', '!=', 2)
    ]).get()
    assert [3, 4, 6, 7] == [x.id for x in posts]
