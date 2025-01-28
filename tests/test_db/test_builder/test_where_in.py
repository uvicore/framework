import pytest
import uvicore
import sqlalchemy as sa
from uvicore.support.dumper import dump

# DB Builder

@pytest.mark.asyncio
async def test_single1(app1):
    query = (uvicore.db.query('app1')
        .table('posts')
        .where('unique_slug', 'in', [
            'test-post1',
            'test-post2',
        ])
    )
    results = await query.get()
    print(query.sql())
    dump(results)
    dump(results[0]._mapping.keys())
    assert ['test-post1', 'test-post2'] == [x.unique_slug for x in results]


@pytest.mark.asyncio
async def test_single2(app1):
    # Single where IN
    posts = await uvicore.db.query().table('posts').where('creator_id', 'in', [1, 2]).get()
    assert [1, 2, 3, 4, 5] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_and(app1):
    # Multiple where IN
    posts = await uvicore.db.query().table('posts').where('creator_id', 'in', [1, 2]).where('owner_id', 'in', [1, 99]).get()
    assert [3, 4] == [x.id for x in posts]

    # Where IN with AND
    posts = await uvicore.db.query().table('posts').where('other', 'null').where('owner_id', 'in', [1, 4]).get()
    assert [4, 7] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_and_or(app1):
    # Where IN with AND OR
    posts = await uvicore.db.query().table('posts').where('creator_id', 'in', [1, 2]).or_where([
        ('unique_slug', 'test-post1'),
        ('unique_slug', 'test-post6'),
    ]).get()
    assert [1] == [x.id for x in posts]


