"""
Web HTTP test harness.

Under pytest the framework forces uvicore.app.is_http = False (see
uvicore/foundation/application.py), so the HTTP bootstrap handler early-returns
and never builds the servers, initializes the templating view paths, or
aggregates each package's view composers into
uvicore.config.uvicore.http.view_composers.

This fixture flips the app into HTTP mode and (re)runs the HTTP bootstrap
handler so the web server, templates and view composers are all wired up, then
restores the original flags.  It is a no-op if the server was already built by
another fixture (e.g. the api test harness) in the same session.
"""
import pytest_asyncio
import uvicore


@pytest_asyncio.fixture(scope="session")
async def webserver(app1):
    if uvicore.app.http is None:
        orig_is_http = uvicore.app.is_http
        orig_is_console = uvicore.app.is_console
        uvicore.app._is_console = False
        uvicore.app._is_http = True
        from uvicore.http.package.bootstrap import Http
        from uvicore.foundation.events.app import Booted
        Http()(Booted())
        uvicore.app._is_http = orig_is_http
        uvicore.app._is_console = orig_is_console

    assert uvicore.app.http is not None, "HTTP server was not built for web tests"
    yield uvicore.app.http
