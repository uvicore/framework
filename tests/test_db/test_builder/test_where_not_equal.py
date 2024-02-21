import pytest
import uvicore
import sqlalchemy as sa
from uvicore.support.dumper import dump

# DB Builder

@pytest.mark.asyncio
async def test_single(app1):
    # Single where NOT
    posts = await uvicore.db.query().table('posts').where('creator_id', '!=', 2).order_by('id').get()
    assert [1, 2, 6, 7] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_and(app1):
    # Multiple where NOT AND
    posts = await uvicore.db.query().table('posts').where('creator_id', '!=', 2).where('owner_id', '!=', 2).order_by('id').get()
    assert [6, 7] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_and_list(app1):
    # Multiple where NOT AND using a LIST
    posts = await uvicore.db.query().table('posts').where([
        ('creator_id', '!=', 2),
        ('owner_id', '!=', 2),
    ]).order_by('id').get()
    assert [6, 7] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_or(app1):
    # Where NOT OR
    posts = await uvicore.db.query().table('posts').or_where([
        ('creator_id', '!=', 1),
        ('owner_id', '!=', 2)
    ]).order_by('id').get()
    assert [3, 4, 5, 6, 7] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_or_and(app1):
    # Where NOT AND with where OR
    posts = await uvicore.db.query().table('posts').where('unique_slug', '!=', 'test-post5').or_where([
        ('creator_id', '!=', 1),
        ('owner_id', '!=', 2)
    ]).order_by('id').get()
    assert [3, 4, 6, 7] == [x.id for x in posts]
