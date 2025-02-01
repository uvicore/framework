import pytest
import uvicore
import sqlalchemy as sa
from uvicore.support.dumper import dump

# DB SQLAlchemy

@pytest.mark.asyncio
async def test_group_by(app1):
    from app1.database.tables.posts import Posts

    posts = Posts.table
    query = (
        sa.select(
            posts.c.creator_id,
            sa.func.count(posts.c.title)
        )
        .group_by(posts.c.creator_id)
    )
    results = await uvicore.db.fetchall(query, connection='app1')
    dump(results)
    dump(results[0]._mapping.keys())
    assert [(1, 2), (2, 3), (5, 1), (6, 1)] == results
