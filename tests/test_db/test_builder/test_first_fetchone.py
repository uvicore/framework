import pytest
import uvicore
import sqlalchemy as sa
from uvicore.support.dumper import dump

# DB Builder

@pytest.mark.asyncio
async def test_first(app1):
    # The .first() and .fetchone() methods are used to get ONE record, the first/top record from the query results.
    # Returns None if no records found.
    posts = await uvicore.db.query().table('posts').order_by('unique_slug').first()
    posts_empty = await uvicore.db.query().table('posts').where('id', 9999).first()

    assert posts.unique_slug == 'test-post1'
    assert posts_empty is None


@pytest.mark.asyncio
async def test_fetchone(app1):
    # The .first() and .fetchone() methods are used to get ONE record, the first/top record from the query results.
    # Returns None if no records found.
    posts = await uvicore.db.query().table('posts').order_by('unique_slug').fetchone()
    posts_empty = await uvicore.db.query().table('posts').where('id', 9999).fetchone()

    assert posts.unique_slug == 'test-post1'
    assert posts_empty is None
