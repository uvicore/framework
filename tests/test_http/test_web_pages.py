"""
End-to-end tests for the app1 server-rendered web pages.

Exercises the rebuilt web surface through the real ASGI stack: template
inheritance (layouts/app.j2), the header/footer/sidebar partials, the Layout +
Sidebar view composers, named-route url() links, asset()/public() static URLs,
custom Jinja processors (shout filter, money context filter, prime test), form
POST handling, redirects, and the custom 404 page.

The `webserver` session fixture (tests/test_http/conftest.py) builds/mounts the
web+api servers; here we bind an httpx AsyncClient to that ASGI app.
"""
import pytest
import pytest_asyncio
import uvicore
from httpx import ASGITransport, AsyncClient


@pytest_asyncio.fixture(scope="session")
async def webclient(webserver):
    async with AsyncClient(transport=ASGITransport(app=webserver), base_url="http://testserver") as client:
        yield client


@pytest.mark.asyncio
async def test_home_page(webclient):
    r = await webclient.get('/')
    assert r.status_code == 200
    body = r.text
    # Layout composer context reached the shared layout
    assert 'Uvicore Web' in body
    # Header partial + named-route nav
    assert 'site-header' in body
    assert 'site-footer' in body
    # Sidebar composer only renders on home/about
    assert 'app1-sidebar' in body
    # Asset + public helpers resolved to the mounted static routes
    assert '/assets/css/app.css' in body
    assert '/assets/js/app.js' in body


@pytest.mark.asyncio
async def test_about_page_has_sidebar(webclient):
    r = await webclient.get('/about')
    assert r.status_code == 200
    assert 'app1-sidebar' in r.text


@pytest.mark.asyncio
async def test_features_page_custom_jinja(webclient):
    r = await webclient.get('/features')
    assert r.status_code == 200
    body = r.text
    # shout filter: 'hello world' | shout -> HELLO WORLD!
    assert 'HELLO WORLD!' in body
    # money context filter: 1299.9 | money -> $1,299.90
    assert '$1,299.90' in body
    # prime test tagged at least one prime number
    assert 'prime' in body


@pytest.mark.asyncio
async def test_contact_get_and_post(webclient):
    r = await webclient.get('/contact')
    assert r.status_code == 200
    assert '<form' in r.text

    r = await webclient.post('/contact', data={
        'name': 'Ada', 'email': 'ada@example.com', 'message': 'Hi',
    })
    assert r.status_code == 200
    # Success alert echoes the submitted values
    assert 'Ada' in r.text
    assert 'ada@example.com' in r.text


@pytest.mark.asyncio
async def test_login_get_and_post(webclient):
    r = await webclient.get('/login')
    assert r.status_code == 200
    assert '<form' in r.text

    r = await webclient.post('/login', data={'username': 'ada', 'password': 'x'})
    assert r.status_code == 200
    assert 'ada' in r.text


@pytest.mark.asyncio
async def test_logout_redirects_home(webclient):
    r = await webclient.get('/logout', follow_redirects=False)
    assert r.status_code in (302, 303, 307)
    assert r.headers['location'].rstrip('/').endswith('testserver') or r.headers['location'] in ('/', 'http://testserver/')


@pytest.mark.asyncio
async def test_about2_plain_text(webclient):
    r = await webclient.get('/about2')
    assert r.status_code == 200
    assert 'About2 plain text here' in r.text


@pytest.mark.asyncio
async def test_custom_404_page(webclient):
    r = await webclient.get('/this-page-does-not-exist')
    assert r.status_code == 404
    # Our standalone errors/404.j2 renders the big code and links home via url()
    assert '404' in r.text
    assert '/assets/css/app.css' in r.text


@pytest.mark.asyncio
async def test_admin_requires_auth(webclient):
    # Anonymous access to the guarded /admin must not return the admin page.
    # Depending on the web auth config it either redirects to login or 401s.
    r = await webclient.get('/admin', follow_redirects=False)
    assert r.status_code != 200
