import pytest
import uvicore
import sqlalchemy as sa
from uvicore.support.dumper import dump

# DB Builder

@pytest.mark.asyncio
async def test_group_by(app1):
    import sqlalchemy as sa
    from app1.database.tables.posts import Posts

    # In order to use any raw SQLAlchemy function, you must get the actual table
    # This is a hybrid because of the count(), but we want to test a STRING order_by
    posts = Posts.table.c

    query = (uvicore.db.query('app1')
        .table('posts')
        .select('creator_id', sa.func.count(posts.id))
        .group_by('creator_id')
    )
    results = await query.get()
    print(query.sql())
    dump(results)
    dump(results[0].keys())
    assert [(1, 2), (2, 3), (5, 1), (6, 1)] == results
