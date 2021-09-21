import pytest
import uvicore
from uvicore.support.dumper import dump

# DB ORM

@pytest.mark.asyncio
async def test_single(app1):
    # Single where IN
    from app1.models.post import Post
    posts = await Post.query().where('creator_id', 'in', [1, 2]).get()
    assert [1, 2, 3, 4, 5] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_and(app1):
    # Multiple where IN
    from app1.models.post import Post
    posts = await Post.query().where('creator_id', 'in', [1, 2]).where('owner_id', 'in', [1, 99]).get()
    assert [3, 4] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_and2(app1):
    # Where IN with AND
    from app1.models.post import Post
    posts = await Post.query().where('other', 'null').where('owner_id', 'in', [1, 4]).get()
    assert [4, 7] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_and_or(app1):
    # Where IN with AND OR
    from app1.models.post import Post
    posts = await Post.query().where('creator_id', 'in', [1, 2]).or_where([
        ('slug', 'test-post1'),
        ('slug', 'test-post6'),
    ]).get()
    assert [1] == [x.id for x in posts]
