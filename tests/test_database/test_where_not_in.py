import pytest
import uvicore
import sqlalchemy as sa
from uvicore.support.dumper import dump


@pytest.mark.asyncio
async def test_orm(app1):
    from app1.models.post import Post

    # Single where NOT IN
    posts = await Post.query().where('creator_id', '!in', [1, 2]).get()
    assert [6, 7] == [x.id for x in posts]

    # Multiple where NOT IN
    posts = await Post.query().where('creator_id', '!in', [1, 2]).where('owner_id', '!in', [3, 99]).get()
    assert [7] == [x.id for x in posts]

    # Where NOT IN with AND
    posts = await Post.query().where('other', '!=', 'null').where('owner_id', '!in', [1, 2]).get()
    assert [6] == [x.id for x in posts]

    # Where NOT IN with AND OR (6,7)
    posts = await Post.query().where('creator_id', '!in', [1, 2]).or_where([
        ('slug', 'test-post6'),
        ('slug', 'test-post2'),
    ]).get()
    assert [6] == [x.id for x in posts]


@pytest.mark.asyncio
async def Xtest_builder(app1):
    # FIXME, make it look exactly like the ORM version above
    pass


@pytest.mark.asyncio
async def Xtest_hybrid(app1):
    # FIXME, make it look exactly like the ORM version above
    pass


@pytest.mark.asyncio
async def Xtest_sqlalchemy(app1):
    # FIXME, make it look exactly like the ORM version above
    pass
