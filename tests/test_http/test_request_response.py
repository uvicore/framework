import pytest
import uvicore
from uvicore.support.dumper import dump


@pytest.mark.asyncio
async def test_http_module_importable(app1):
    """Test that http module is importable"""
    from uvicore import http
    assert http is not None


@pytest.mark.asyncio
async def test_request_class_exists(app1):
    """Test that Request class exists"""
    from uvicore.http import Request
    assert Request is not None


@pytest.mark.asyncio
async def test_guard_class_exists(app1):
    """Test that Guard class exists"""
    from uvicore.http.routing import Guard
    assert Guard is not None

