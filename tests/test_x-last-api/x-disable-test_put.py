import pytest
import uvicore
from uvicore.support.dumper import dump
from tests.seeders import seed_post8

# PUT is a complete update to a single item only /{id}, not multiples
# PUT must be complete, not partial.  The entire record is replaced with the one in the body

@pytest.mark.asyncio
async def test_single(app1, client):
    # Update a single, complete item /{id} in url, NO relations
    from app1.models import Post

    # Create a temp post we can delete
    await seed_post8()
    post = await Post.query().find(slug='test-post8')
    dump(post)

    assert False
