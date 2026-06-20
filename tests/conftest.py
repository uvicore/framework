import pytest
import uvicore
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from uvicore.typing import Generator
from uvicore.support.dumper import dump, dd


# NOTE: pytest-asyncio 1.x removed support for overriding the `event_loop`
# fixture.  The single session-wide loop is now configured declaratively via
# [tool.pytest.ini_options] asyncio_default_{fixture,test}_loop_scope = "session"
# in pyproject.toml, so no custom event_loop fixture is needed (or allowed) here.


@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def app1():

    #import sys
    #dd(sys.modules)

    # Setup Tests
    ############################################################################
    # Bootstrap uvicore application
    from app1.package import bootstrap
    bootstrap.Application(is_console=False)()

    # Register a PytestStartup event (uvicore.console.events.command.PytestStartup)
    # Which is listened to by database/db.py to connect to all dbs
    from uvicore.console.events import command as ConsoleEvents
    await ConsoleEvents.PytestStartup().codispatch()

    # Drop/Create and Seed SQLite In-Memory Database
    from uvicore.database.commands import db
    await db.drop_tables('app1')
    await db.create_tables('app1')
    await db.seed_tables('app1')

    #from app1.database.seeders import seed
    #engine = uvicore.db.engine()
    #metadata = uvicore.db.metadata()
    #metadata.drop_all(engine)
    #metadata.create_all(engine)
    #await seed()


    # Run ALL Tests
    ############################################################################

    yield ''


    # Tear down tests
    ############################################################################
    #metadata.drop_all(engine)

    # Register a PytestShutdown event (uvicore.console.events.command.PytestShutdown) to disconnect from all DBs
    await ConsoleEvents.PytestShutdown().codispatch()



# Async TestClient based on encode/httpx
# https://github.com/tiangolo/fastapi/issues/1273
@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def client() -> Generator:
    async with AsyncClient(transport=ASGITransport(app=uvicore.app.http), base_url="http://testserver") as client:
        yield client
