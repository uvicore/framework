import pytest
import uvicore
import sqlalchemy as sa
from uvicore.support.dumper import dump

# DB Builder

@pytest.mark.asyncio
async def test_order_by_desc(app1):
    query = (uvicore.db.query('app1')
        .table('posts')
        .order_by('id', 'DESC')
    )
    results = await query.get()
    print(query.sql())
    dump(results)
    dump(results[0].keys())
    assert [
        'test-post7',
        'test-post6',
        'test-post5',
        'test-post4',
        'test-post3',
        'test-post2',
        'test-post1',
    ] == [x.unique_slug for x in results]


@pytest.mark.asyncio
async def test_order_by_asc(app1):
    query = (uvicore.db.query('app1')
        .table('posts')
        .order_by('owner_id', 'ASC')
    )
    results = await query.get()
    print(query.sql())
    dump(results)
    dump(results[0].keys())
    assert [
        'test-post3',
        'test-post4',
        'test-post1',
        'test-post2',
        'test-post5',
        'test-post6',
        'test-post7',
    ] == [x.unique_slug for x in results]


@pytest.mark.asyncio
async def test_order_by_list_multiples(app1):
    # Notice one is no order (default ASC, one defines order DESC, this is for code coverage)
    query = (uvicore.db.query('app1')
        .table('posts')
        .order_by([
            ('creator_id'),
            ('owner_id', 'DESC')
        ])
    )
    results = await query.get()
    print(query.sql())
    dump(results)
    dump(results[0].keys())
    assert [
        'test-post1',
        'test-post2',
        'test-post5',
        'test-post3',
        'test-post4',
        'test-post7',
        'test-post6',
    ] == [x.unique_slug for x in results]


@pytest.mark.asyncio
async def test_order_by_list_multiples_bad_tuple(app1):
    # This one has the order_by of ('creator_id',) just for code coverage
    query = (uvicore.db.query('app1')
        .table('posts')
        .order_by([
            ('creator_id',),
            ('owner_id', 'DESC')
        ])
    )
    results = await query.get()
    print(query.sql())
    dump(results)
    dump(results[0].keys())
    assert [
        'test-post1',
        'test-post2',
        'test-post5',
        'test-post3',
        'test-post4',
        'test-post7',
        'test-post6',
    ] == [x.unique_slug for x in results]
