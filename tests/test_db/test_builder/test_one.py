import pytest
import uvicore
import sqlalchemy as sa
from uvicore.support.dumper import dump

# DB Builder

# The .one() method is used to get one record from query or an Exception if not found.
# Throws an Exception if no data found or querying more than one record.
# If ID 4 exists, returns result. If ID 4 does not exist, throws Exception: No row was found when one was required

@pytest.mark.asyncio
async def test_one(app1):
    posts = await uvicore.db.query().table('posts').where('id', 4).one()
    dump(posts)
    assert posts.unique_slug == 'test-post4'


@pytest.mark.asyncio
async def test_one_exception(app1):
    with pytest.raises(Exception) as e:
        posts = await uvicore.db.query().table('posts').where('id', 9999).one()
    assert 'No row was found' in str(e)


@pytest.mark.asyncio
async def test_one_multiples(app1):
    with pytest.raises(Exception) as e:
        posts = await uvicore.db.query().table('posts').where('id', '>', 1).one()
    assert 'Multiple rows were found' in str(e)
