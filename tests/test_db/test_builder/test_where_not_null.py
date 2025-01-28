import pytest
import uvicore
import sqlalchemy as sa
from uvicore.support.dumper import dump

# DB Builder

@pytest.mark.asyncio
async def test_where_not_null(app1):
    query = (uvicore.db.query('app1')
        .table('posts')
        .where('other', '!=', 'null')
    )
    results = await query.get()
    print(query.sql())
    dump(results)
    dump(results[0]._mapping.keys())
    assert ['test-post1', 'test-post3', 'test-post6'] == [x.unique_slug for x in results]
