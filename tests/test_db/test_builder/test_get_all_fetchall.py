import pytest
import uvicore
import sqlalchemy as sa
from uvicore.support.dumper import dump

# DB Builder

@pytest.mark.asyncio
async def test_get(app1):
    # The .get(), .all() and .fetchall() methods are used to get one or more records.
    # Returns a List[Row] or an empty List [] if no results found.
    posts = await uvicore.db.query().table('posts').order_by('unique_slug').get()
    posts_empty = await uvicore.db.query().table('posts').where('id', '>', 9999).get()
    dump(posts)

    assert ['test-post1','test-post2','test-post3','test-post4','test-post5','test-post6','test-post7'] == [x.unique_slug for x in posts]
    assert posts_empty == []

@pytest.mark.asyncio
async def test_all(app1):
    # The .get(), .all() and .fetchall() methods are used to get one or more records.
    # Returns a List[Row] or an empty List [] if no results found.
    posts = await uvicore.db.query().table('posts').order_by('unique_slug').all()
    posts_empty = await uvicore.db.query().table('posts').where('id', '>', 9999).all()
    dump(posts)

    assert ['test-post1','test-post2','test-post3','test-post4','test-post5','test-post6','test-post7'] == [x.unique_slug for x in posts]
    assert posts_empty == []


@pytest.mark.asyncio
async def test_fetchall(app1):
    # The .get(), .all() and .fetchall() methods are used to get one or more records.
    # Returns a List[Row] or an empty List [] if no results found.
    posts = await uvicore.db.query().table('posts').order_by('unique_slug').fetchall()
    posts_empty = await uvicore.db.query().table('posts').where('id', '>', 9999).fetchall()
    dump(posts)

    assert ['test-post1','test-post2','test-post3','test-post4','test-post5','test-post6','test-post7'] == [x.unique_slug for x in posts]
    assert posts_empty == []




