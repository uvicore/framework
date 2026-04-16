import pytest
import uvicore
import sqlalchemy as sa
from uvicore.support.dumper import dump

# DB Builder

# The .scalar() method is used to get one column from one row.
# Returns None if no record found. Returns first column from first row if more than one record found.

@pytest.mark.asyncio
async def test_scalar(app1):
    posts = await uvicore.db.query().table('posts').select('unique_slug').where('id', '>', 2).order_by('unique_slug').scalar()
    assert posts == 'test-post3'


@pytest.mark.asyncio
async def test_scalar_multicol(app1):
    posts = await uvicore.db.query().table('posts').select('unique_slug', 'title', 'id').where('id', '>', 2).order_by('unique_slug').scalar()
    assert posts == 'test-post3'


@pytest.mark.asyncio
async def test_scalar_star(app1):
    posts = await uvicore.db.query().table('posts').where('id', '>', 2).order_by('unique_slug').scalar()
    assert posts == 3


@pytest.mark.asyncio
async def test_scalar_none(app1):
    posts = await uvicore.db.query().table('posts').where('id', '>', 9999).scalar()
    dump(posts)
    assert posts is None
