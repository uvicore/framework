import pytest
import uvicore
from uvicore.support.dumper import dump


@pytest.mark.asyncio
async def test_request_class_importable(app1):
    """Test Request class can be imported"""
    from uvicore.http.request import Request
    assert Request is not None


@pytest.mark.asyncio
async def test_request_attributes(app1):
    """Test Request has expected attributes"""
    from uvicore.http.request import Request
    # Request should be a class with methods
    assert hasattr(Request, '__init__')


@pytest.mark.asyncio
async def test_response_module_importable(app1):
    """Test response module can be imported"""
    from uvicore.http import response
    assert response is not None


@pytest.mark.asyncio
async def test_response_classes(app1):
    """Test response classes exist"""
    from uvicore.http.response import View, JSON
    assert View is not None
    assert JSON is not None


@pytest.mark.asyncio
async def test_status_codes_available(app1):
    """Test HTTP status codes"""
    from uvicore.http import status
    assert status is not None


@pytest.mark.asyncio
async def test_http_exceptions_available(app1):
    """Test HTTP exception classes"""
    from uvicore.http.exceptions import HTTPException, NotFound
    assert HTTPException is not None
    assert NotFound is not None


@pytest.mark.asyncio
async def test_request_exception_raising(app1):
    """Test raising HTTPException"""
    from uvicore.http.exceptions import NotFound
    with pytest.raises(NotFound):
        raise NotFound("Resource not found")
