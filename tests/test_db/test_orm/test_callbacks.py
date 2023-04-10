import pytest
import uvicore
from uvicore.support.dumper import dump


@pytest.mark.asyncio
async def test_callback(app1):
    from app1.models.post import Post
    post: PostModel = await Post.query().find(2)
    dump(post)
    assert post.cb == 'test-post2 callback'
