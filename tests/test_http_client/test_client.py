import pytest
import uvicore
from uvicore.support.dumper import dump


@pytest.mark.asyncio
async def test_http_client_module_exists(app1):
    """Test http_client module"""
    from uvicore import http_client
    assert http_client is not None
