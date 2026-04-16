import pytest
import uvicore
import sqlalchemy as sa
from uvicore.support.dumper import dump

# DB Builder

# The .scalars() (plural) method is used to get one column from ALL rows in results.
# Returns empty List [] if no records found. If selecting multiple columns, returns List of FIRST column only.

@pytest.mark.asyncio
async def test_scalars(app1):
    posts = await uvicore.db.query().table('posts').select('unique_slug').where('id', '>', 2).order_by('unique_slug').scalars()
    dump(posts)
    assert posts == ['test-post3','test-post4','test-post5','test-post6','test-post7']


@pytest.mark.asyncio
async def test_scalars_multicol(app1):
    posts = await uvicore.db.query().table('posts').select('unique_slug', 'title', 'id').where('id', '>', 2).order_by('unique_slug').scalars()
    dump(posts)
    assert posts == ['test-post3','test-post4','test-post5','test-post6','test-post7']


@pytest.mark.asyncio
async def test_scalars_star(app1):
    # If no column specified, uses first column (ID in this case)
    posts = await uvicore.db.query().table('posts').where('id', '>', 2).order_by('unique_slug').scalars()
    dump(posts)
    assert posts == [3, 4, 5, 6, 7]


@pytest.mark.asyncio
async def test_scalars_none(app1):
    posts = await uvicore.db.query().table('posts').where('id', '>', 9999).scalars()
    dump(posts)
    assert posts == []
