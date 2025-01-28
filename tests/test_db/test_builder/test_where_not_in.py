import pytest
import uvicore
import sqlalchemy as sa
from uvicore.support.dumper import dump

# DB Builder

@pytest.mark.asyncio
async def test_where_not_in(app1):
    query = (uvicore.db.query('app1')
        .table('posts')
        .where('unique_slug', '!in', [
            'test-post1',
            'test-post2',
            'test-post5',
        ])
    )
    results = await query.get()
    print(query.sql())
    dump(results)
    dump(results[0]._mapping.keys())
    assert ['test-post3', 'test-post4', 'test-post6', 'test-post7'] == [x.unique_slug for x in results]
