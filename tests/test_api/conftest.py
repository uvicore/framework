"""
Live HTTP API test harness.

Under pytest, the framework forces uvicore.app.is_http = False (see
uvicore/foundation/application.py), so the HTTP bootstrap handler early-returns
and never builds/mounts the Starlette+FastAPI server. That makes uvicore.app.http
unusable and is why the older client-based API tests were all disabled.

This fixture flips the app into HTTP mode, re-runs the HTTP bootstrap handler to
actually build and mount the web + api servers, then restores the original flags
(the built server persists on uvicore.app._http). It yields a working httpx
AsyncClient bound directly to the ASGI app so we can exercise the real API,
the auto-API ModelRouter, route Guards/scopes, the auth middleware and the
exception handlers end to end.
"""
import base64
import pytest_asyncio
import uvicore
from httpx import AsyncClient


@pytest_asyncio.fixture(scope="session")
async def apiclient(app1):
    # Save original (pytest) flags
    orig_is_http = uvicore.app.is_http
    orig_is_console = uvicore.app.is_console

    # Flip into HTTP mode and (re)build the HTTP server. build_package_routes()
    # inside the handler now imports the package routes (gated on is_http) and
    # create_http_servers() mounts the web/api subservers onto a base Starlette app.
    uvicore.app._is_console = False
    uvicore.app._is_http = True
    from uvicore.http.package.bootstrap import Http
    from uvicore.foundation.events.app import Booted
    Http()(Booted())

    # Restore original flags so the rest of the suite sees the normal pytest state.
    # The built server remains attached at uvicore.app._http.
    uvicore.app._is_http = orig_is_http
    uvicore.app._is_console = orig_is_console

    assert uvicore.app.http is not None, "HTTP server was not built for API tests"

    async with AsyncClient(app=uvicore.app.http, base_url="http://testserver") as client:
        yield client


def basic_auth(username: str, password: str) -> dict:
    """Build an HTTP Basic Authorization header dict."""
    token = base64.b64encode(f"{username}:{password}".encode()).decode()
    return {"Authorization": "Basic " + token}
