"""
Live HTTP tests for the automatic model CRUD API (ModelRouter / auto_api).

These exercise uvicore/http/routing/model_router.py, auto_api.py, response.py and
the ORM query path end to end through the real ASGI server. The app1 test app
registers the auto API with open scopes (api.auto_api.scopes = []), so these
read endpoints need no authentication.
"""
import pytest


@pytest.mark.asyncio
async def test_list_all_posts(apiclient):
    """GET /api/posts returns all seeded posts as a JSON list."""
    res = await apiclient.get('/api/posts')
    assert res.status_code == 200, res.text
    posts = res.json()
    assert isinstance(posts, list)
    assert len(posts) == 7
    # Each row has the expected scalar fields
    first = posts[0]
    for key in ('id', 'slug', 'title', 'body', 'creator_id'):
        assert key in first


@pytest.mark.asyncio
async def test_find_by_primary_key(apiclient):
    """GET /api/posts/{id} returns the single matching record."""
    res = await apiclient.get('/api/posts/1')
    assert res.status_code == 200, res.text
    post = res.json()
    assert post['id'] == 1
    assert post['slug'] == 'test-post1'


@pytest.mark.asyncio
async def test_find_missing_returns_404(apiclient):
    """GET /api/posts/{id} for a non-existent id returns a 404 (not a 500)."""
    res = await apiclient.get('/api/posts/99999')
    assert res.status_code == 404
    # ModelRouter find raises NotFound -> API exception handler JSON
    body = res.json()
    assert 'not found' in (body.get('message') or body.get('detail') or '').lower()


@pytest.mark.asyncio
async def test_pagination_limits_results(apiclient):
    """page_size limits the number of returned rows."""
    res = await apiclient.get('/api/posts?page=1&page_size=2')
    assert res.status_code == 200, res.text
    assert len(res.json()) == 2

    res = await apiclient.get('/api/posts?page=1&page_size=3')
    assert res.status_code == 200, res.text
    assert len(res.json()) == 3


@pytest.mark.asyncio
async def test_pagination_pages_differ(apiclient):
    """Different pages return different records (offset applied)."""
    page1 = (await apiclient.get('/api/posts?page=1&page_size=2&order_by=id')).json()
    page2 = (await apiclient.get('/api/posts?page=2&page_size=2&order_by=id')).json()
    assert len(page1) == 2 and len(page2) == 2
    page1_ids = {p['id'] for p in page1}
    page2_ids = {p['id'] for p in page2}
    assert page1_ids.isdisjoint(page2_ids)
