import pytest
import sqlalchemy as sa

import uvicore
from uvicore.support.dumper import dump


@pytest.mark.asyncio
async def test_orm(app1):
    from app1.models.post import Post

    post = await Post.query().include('image').find(1)
    dump(post)
    assert False
