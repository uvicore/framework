import pytest
import uvicore
import sqlalchemy as sa
from uvicore.support.dumper import dump

# DB Builder

# The .one_or_none() method is used to get one record from query or None if nothing found.
# Returns None if no record found or Throws Exception if querying more than one record.

@pytest.mark.asyncio
async def test_one_or_none(app1):
    posts = await uvicore.db.query().table('posts').where('id', 4).one_or_none()
    dump(posts)
    assert posts.unique_slug == 'test-post4'


@pytest.mark.asyncio
async def test_one_or_none_empty(app1):
    posts = await uvicore.db.query().table('posts').where('id', 9999).one_or_none()
    dump(posts)
    assert posts is None


@pytest.mark.asyncio
async def test_one_or_none_multiples(app1):
    with pytest.raises(Exception) as e:
        posts = await uvicore.db.query().table('posts').where('id', '>', 1).one_or_none()
    assert 'Multiple rows were found' in str(e)
