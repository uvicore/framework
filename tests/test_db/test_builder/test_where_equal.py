import pytest
import uvicore
import sqlalchemy as sa
from uvicore.support.dumper import dump

# DB Builder

@pytest.mark.asyncio
async def test_single(app1):
    # Single where
    query = uvicore.db.query('app1').table('posts').where('creator_id', 2)
    posts = await query.get()
    #print(query.sql());dump(posts); dump(posts[0]._mapping.keys())
    assert [3, 4, 5] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_and(app1):
    # Multiple where AND
    query = uvicore.db.query().table('posts').where('creator_id', '=', 2).where('owner_id', 1)
    posts = await query.get()
    #print(query.sql());dump(posts); dump(posts[0]._mapping.keys())
    assert [3, 4] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_and_list(app1):
    # Multiple where AND using a LIST
    posts = await uvicore.db.query().table('posts').where([
        ('creator_id', '=', 2),
        ('owner_id', 1),
    ]).get()
    assert [3, 4] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_or(app1):
    # Where OR
    posts = await uvicore.db.query().table('posts').or_where([
        ('unique_slug', 'test-post3'),
        ('unique_slug', '=', 'test-post4'),
    ]).get()
    assert [3, 4] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_and_or(app1):
    # Where AND with where OR
    posts = await uvicore.db.query().table('posts').where('creator_id', '=', 2).or_where([
        ('unique_slug', 'test-post3'),
        ('unique_slug', '=', 'test-post4'),
    ]).get()
    assert [3, 4] == [x.id for x in posts]
