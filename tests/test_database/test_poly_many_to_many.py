import pytest
import uvicore
import sqlalchemy as sa
from uvicore.support.dumper import dump


@pytest.mark.asyncio
async def test_orm(app1):
    # The only example of a Polymorphic Many-To-Many is the hashtag table

    # FIXME, never done

    from app1.models.post import Post

    query = Post.query().include('attributes')

    sql = query.sql()
    dump(sql)

    posts = await query.get()

    dump(posts)

    assert False



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
