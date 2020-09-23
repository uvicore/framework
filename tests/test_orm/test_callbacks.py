import pytest
import uvicore
from typing import List
from uvicore.support.dumper import dump
from starlette.testclient import TestClient

# Typechecking imports only
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app1.models.post import PostModel


@pytest.mark.asyncio
async def test_callback(bootstrap_app1):
    from app1.models.post import Post
    post: PostModel = await Post.find(2)
    assert post.cb == 'test-post2 callback'
