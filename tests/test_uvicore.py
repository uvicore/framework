import pytest
import uvicore
from uvicore.support.dumper import dump, dd
from starlette.testclient import TestClient



@pytest.mark.asyncio
async def test_app1(app1):

    dump(uvicore.db.packages('app1'))

    assert False


