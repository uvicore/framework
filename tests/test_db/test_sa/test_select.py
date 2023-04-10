import pytest
import uvicore
import sqlalchemy as sa
from uvicore.support.dumper import dump

# DB SQLAlchemy

@pytest.mark.asyncio
async def test_select_all(app1):
    from app1.database.tables.posts import Posts

    query = Posts.table.select()
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
