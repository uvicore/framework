"""
Live HTTP tests for route Guards, scopes and the Authentication middleware.

These exercise the security-critical paths that were previously untested:
  - uvicore/http/routing/guard.py (Scopes dependency, AND-scope enforcement)
  - uvicore/http/middleware/authentication.py (loads request.user, anonymous fallback)
  - uvicore/auth/authenticators/basic.py (HTTP Basic auth)

The app1 test app exposes:
  - GET /api/ping     -> guarded, requires the 'posts.read' permission
  - GET /api/public   -> open, echoes request.user (anonymous when unauthenticated)

Seeded users (password 'techie'):
  - manager1@example.com -> role 'Post Users' (has posts.read)
  - user1@example.com    -> no roles (authenticated but no permissions)
"""
import pytest
from tests.test_api.conftest import basic_auth


@pytest.mark.asyncio
async def test_protected_route_requires_authentication(apiclient):
    """Anonymous request to a guarded route is rejected with 401."""
    res = await apiclient.get('/api/ping')
    assert res.status_code == 401, res.text
    assert res.json()['message'] == 'Not Authenticated'


@pytest.mark.asyncio
async def test_protected_route_allows_user_with_permission(apiclient):
    """A user holding the required 'posts.read' scope is allowed through."""
    res = await apiclient.get('/api/ping', headers=basic_auth('manager1@example.com', 'techie'))
    assert res.status_code == 200, res.text
    assert 'pong' in res.json()['message']


@pytest.mark.asyncio
async def test_authenticated_user_without_permission_is_denied(apiclient):
    """An authenticated user lacking the scope is denied.

    Uvicore returns 401 for authorization failures too, but distinguishes the
    cause from the anonymous case via the message: 'Permission Denied' (the user
    IS authenticated) vs 'Not Authenticated' (no/invalid credentials).
    """
    res = await apiclient.get('/api/ping', headers=basic_auth('user1@example.com', 'techie'))
    assert res.status_code == 401, res.text
    assert res.json()['message'] == 'Permission Denied'


@pytest.mark.asyncio
async def test_bad_password_is_rejected(apiclient):
    """Wrong credentials do not authenticate; the guarded route stays protected (401)."""
    res = await apiclient.get('/api/ping', headers=basic_auth('manager1@example.com', 'wrongpass'))
    assert res.status_code == 401, res.text


@pytest.mark.asyncio
async def test_public_route_injects_anonymous_user(apiclient):
    """The auth middleware injects an anonymous user on open routes."""
    res = await apiclient.get('/api/public')
    assert res.status_code == 200, res.text
    user = res.json()['user']
    assert user is not None
    assert user['username'] == 'anonymous'
    assert user['email'] == 'anonymous@example.com'


@pytest.mark.asyncio
async def test_public_route_with_valid_login_identifies_user(apiclient):
    """Valid Basic auth on an open route resolves the real (non-anonymous) user."""
    res = await apiclient.get('/api/public', headers=basic_auth('manager1@example.com', 'techie'))
    assert res.status_code == 200, res.text
    user = res.json()['user']
    assert user['email'] == 'manager1@example.com'
    assert user['username'] != 'anonymous'
