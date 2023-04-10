import pytest
import uvicore
import sqlalchemy as sa
from uvicore.support.dumper import dump

# DB SQLAlchemy

@pytest.mark.asyncio
async def test_order_by_asc(app1):
    from app1.database.tables.posts import Posts

    query = Posts.table.select().order_by(Posts.table.c.id)
    results = await uvicore.db.fetchall(query, connection='app1')
    dump(results)
    assert [
        'test-post1',
        'test-post2',
        'test-post3',
        'test-post4',
        'test-post5',
        'test-post6',
        'test-post7'
    ] == [x.unique_slug for x in results]


@pytest.mark.asyncio
async def test_order_by_asc_explicit(app1):
    from app1.database.tables.posts import Posts

    query = Posts.table.select().order_by(sa.asc(Posts.table.c.id))
    results = await uvicore.db.fetchall(query, connection='app1')
    dump(results)
    assert [
        'test-post1',
        'test-post2',
        'test-post3',
        'test-post4',
        'test-post5',
        'test-post6',
        'test-post7'
    ] == [x.unique_slug for x in results]


@pytest.mark.asyncio
async def test_order_by_desc(app1):
    from app1.database.tables.posts import Posts

    query = Posts.table.select().order_by(sa.desc(Posts.table.c.id))
    results = await uvicore.db.fetchall(query, connection='app1')
    dump(results)
    assert [
        'test-post7',
        'test-post6',
        'test-post5',
        'test-post4',
        'test-post3',
        'test-post2',
        'test-post1'
    ] == [x.unique_slug for x in results]
