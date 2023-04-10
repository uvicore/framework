import pytest
import uvicore
import sqlalchemy as sa
from uvicore.support.dumper import dump

# DB Hybrid

@pytest.mark.asyncio
async def test_group_by(app1):
    import sqlalchemy as sa
    from app1.database.tables.posts import Posts

    # You can use any SQLAlchemy Core Generic Function (sa.func.xyz) in a select statement
    # as long as you get the actual Table.c (Posts.table.c)
    posts = Posts.table.c
    query = (uvicore.db.query('app1')
        .table(Posts.table)
        .select(posts.creator_id, sa.func.count(posts.id))  # Or can leave blank for *
        #.select(posts.creator_id, sa.func.count(posts.id).label('cnt'))  # Can label it too, defaults to count_1
        .group_by(posts.creator_id)
    )
    results = await query.get()
    print(query.sql())
    dump(results)
    dump(results[0].keys())
    assert [(1, 2), (2, 3), (5, 1), (6, 1)] == results
