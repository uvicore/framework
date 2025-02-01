import pytest
import uvicore
import sqlalchemy as sa
from uvicore.support.dumper import dump

# DB Hybrid

@pytest.mark.asyncio
async def test_or_where_column(app1):
    from app1.database.tables.posts import Posts

    # Test OR where as SQLAlchemy Column name but still parameter based
    posts = Posts.table.c
    query = (uvicore.db.query('app1')
        .table(Posts.table)
        .or_where([
            (posts.creator_id, '=', 2),
            (posts.unique_slug, 'test-post1'),
        ])
    )
    results = await query.get()
    print(query.sql())
    dump(results)
    dump(results[0]._mapping.keys())
    assert ['test-post1', 'test-post3', 'test-post4', 'test-post5'] == [x.unique_slug for x in results]
    #assert 1 == 2


@pytest.mark.asyncio
async def test_or_where_expression(app1):
    from app1.database.tables.posts import Posts

    # Test OR where as SQLAlchemy Binary Expression
    posts = Posts.table.c
    query = (uvicore.db.query('app1')
        .table(Posts.table)
        .or_where([
            posts.creator_id == 2,
            posts.unique_slug == 'test-post1',
        ])
    )
    results = await query.get()
    print(query.sql())
    dump(results)
    dump(results[0]._mapping.keys())
    assert ['test-post1', 'test-post3', 'test-post4', 'test-post5'] == [x.unique_slug for x in results]

