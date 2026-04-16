import pytest
import uvicore
import sqlalchemy as sa
from uvicore.support.dumper import dump

# DB Builder

# The .scalar_one() method is used to get one column from one row or an Exception if not found.
# Throws an Exception if no data found or querying more than one record.

@pytest.mark.asyncio
async def test_scalar_one(app1):
    posts = await uvicore.db.query().table('posts').select('unique_slug').where('id', 2).order_by('unique_slug').scalar_one()
    assert posts == 'test-post2'


@pytest.mark.asyncio
async def test_scalar_one_multicol(app1):
    posts = await uvicore.db.query().table('posts').select('unique_slug', 'title', 'id').where('id', 2).order_by('unique_slug').scalar_one()
    assert posts == 'test-post2'


@pytest.mark.asyncio
async def test_scalar_one_star(app1):
    posts = await uvicore.db.query().table('posts').where('id', 2).order_by('unique_slug').scalar_one()
    assert posts == 2


@pytest.mark.asyncio
async def test_scalar_one_multirow(app1):
    with pytest.raises(Exception) as e:
        posts = await uvicore.db.query().table('posts').where('id', '>', 2).order_by('unique_slug').scalar_one()
    assert 'Multiple rows were found' in str(e)


@pytest.mark.asyncio
async def test_scalar_one_empty(app1):
    with pytest.raises(Exception) as e:
        posts = await uvicore.db.query().table('posts').where('id', 9999).order_by('unique_slug').scalar_one()
    assert 'No row was found' in str(e)
