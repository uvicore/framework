import pytest
import uvicore
import sqlalchemy as sa
from uvicore.support.dumper import dump

# DB Hybrid

@pytest.mark.asyncio
async def test_select_max(app1):
    import sqlalchemy as sa
    from app1.database.tables.posts import Posts

    posts = Posts.table.c
    query = (uvicore.db.query('app1')
        .table(Posts.table)
        .select(sa.func.max(posts.id))
    )
    results = await query.get()
    print(query.sql())
    dump(results)
    dump(results[0]._mapping.keys())
    assert [(7,)] == results
