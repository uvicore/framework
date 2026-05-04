import pytest
import uvicore
from uvicore.support.dumper import dump


@pytest.mark.asyncio
async def test_http_routing_classes_available(app1):
    """Test HTTP routing classes available"""
    from uvicore.http.routing import ApiRouter, Controller
    assert ApiRouter is not None
    assert Controller is not None


@pytest.mark.asyncio
async def test_http_models_request(app1):
    """Test HTTP Request class"""
    from uvicore.http import Request
    assert Request is not None


@pytest.mark.asyncio
async def test_http_models_response_classes(app1):
    """Test HTTP response Classes"""
    from uvicore.http.response import View, JSON, Text, HTML
    assert View is not None
    assert JSON is not None
    assert Text is not None
    assert HTML is not None
