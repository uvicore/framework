import pytest
import asyncio
import uvicore
import pytest_asyncio
from httpx import AsyncClient
from uvicore.typing import Generator
from uvicore.support.dumper import dump, dd


@pytest.fixture(scope='session')
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def app1(event_loop):

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
@pytest_asyncio.fixture(scope="session")
async def client() -> Generator:
    async with AsyncClient(app=uvicore.app.http, base_url="http://testserver") as client:
    #async with AsyncClient(transport=uvicore.app.http, base_url="http://testserver") as client:
        yield client
