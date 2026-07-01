import pytest
import uvicore
from uvicore.support.dumper import dump


@pytest.mark.asyncio
async def test_api_router_exists(app1):
    """Test that ApiRouter class exists"""
    from uvicore.http.routing import ApiRouter
    assert ApiRouter is not None


@pytest.mark.asyncio
async def test_web_router_exists(app1):
    """Test that WebRouter class exists"""
    from uvicore.http.routing import WebRouter
    assert WebRouter is not None


@pytest.mark.asyncio
async def test_controller_exists(app1):
    """Test that Controller class exists"""
    from uvicore.http.routing import Controller
    assert Controller is not None

