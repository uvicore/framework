import pytest
import uvicore
from uvicore.support.dumper import dump

# DB ORM

@pytest.mark.asyncio
async def test_single(app1):
    # Single where NOT IN
    from app1.models.post import Post
    posts = await Post.query().where('creator_id', '!in', [1, 2]).order_by('id').get()
    assert [6, 7] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_and(app1):
    # Multiple where NOT IN
    from app1.models.post import Post
    posts = await Post.query().where('creator_id', '!in', [1, 2]).where('owner_id', '!in', [3, 99]).order_by('id').get()
    assert [7] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_and2(app1):
    # Where NOT IN with AND
    from app1.models.post import Post
    posts = await Post.query().where('other', '!=', 'null').where('owner_id', '!in', [1, 2]).order_by('id').get()
    assert [6] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_and_or(app1):
    # Where NOT IN with AND OR (6,7)
    from app1.models.post import Post
    posts = await Post.query().where('creator_id', '!in', [1, 2]).or_where([
        ('slug', 'test-post6'),
        ('slug', 'test-post2'),
    ]).order_by('id').get()
    assert [6] == [x.id for x in posts]
