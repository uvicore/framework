"""
Live HTTP tests for the auto-API query string parsing (where / include / order_by).

These exercise uvicore/http/routing/auto_api.py (_build_whereable, _build_include,
_build_sortable) and the ORM query builder through the real server. Query params
use the List/JSON format the current API expects, e.g. where=["field", value] or
where=["field", "op", value].
"""
import pytest


@pytest.mark.asyncio
async def test_where_equals(apiclient):
    """where=["creator_id", 1] filters to matching rows."""
    res = await apiclient.get('/api/posts?where=["creator_id",1]')
    assert res.status_code == 200, res.text
    posts = res.json()
    assert len(posts) > 0
    assert all(p['creator_id'] == 1 for p in posts)


@pytest.mark.asyncio
async def test_where_in_operator(apiclient):
    """where=["creator_id", "in", [1,5]] uses the IN operator."""
    res = await apiclient.get('/api/posts?where=["creator_id","in",[1,5]]')
    assert res.status_code == 200, res.text
    posts = res.json()
    assert len(posts) > 0
    assert all(p['creator_id'] in (1, 5) for p in posts)


@pytest.mark.asyncio
async def test_where_like_operator_runs(apiclient):
    """LIKE operator parses and executes (result set may vary by seed data)."""
    res = await apiclient.get('/api/posts?where=["body","like","%post%"]')
    assert res.status_code == 200, res.text
    assert isinstance(res.json(), list)


@pytest.mark.asyncio
async def test_include_relation_is_populated(apiclient):
    """include=creator eager-loads the BelongsTo relation as a nested object."""
    res = await apiclient.get('/api/posts?include=creator&where=["creator_id",1]')
    assert res.status_code == 200, res.text
    posts = res.json()
    assert len(posts) > 0
    creator = posts[0]['creator']
    assert isinstance(creator, dict)
    assert creator.get('id') == 1


@pytest.mark.asyncio
async def test_order_by_descending(apiclient):
    """order_by=["id","DESC"] sorts results descending."""
    res = await apiclient.get('/api/posts?order_by=["id","DESC"]')
    assert res.status_code == 200, res.text
    ids = [p['id'] for p in res.json()]
    assert ids == sorted(ids, reverse=True)
    assert ids[0] == max(ids)


@pytest.mark.asyncio
async def test_order_by_ascending_shorthand(apiclient):
    """order_by=id (shorthand string) sorts ascending."""
    res = await apiclient.get('/api/posts?order_by=id')
    assert res.status_code == 200, res.text
    ids = [p['id'] for p in res.json()]
    assert ids == sorted(ids)


@pytest.mark.asyncio
async def test_invalid_where_returns_400(apiclient):
    """A malformed where (legacy dict format) returns a clean 400 BadParameter, not a 500."""
    res = await apiclient.get('/api/posts?where={"creator_id":1}')
    assert res.status_code == 400, res.text
    body = res.json()
    assert body.get('message') == 'Bad Parameter'
