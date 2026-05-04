import pytest
import uvicore
from uvicore.support.dumper import dump


@pytest.mark.asyncio
async def test_http_exceptions_module_exists(app1):
    """Test HTTP exceptions module"""
    from uvicore.http import exceptions
    assert exceptions is not None


@pytest.mark.asyncio
async def test_http_exception_base(app1):
    """Test HTTPException base class"""
    from uvicore.http.exceptions import HTTPException
    assert HTTPException is not None


@pytest.mark.asyncio
async def test_not_found_exception(app1):
    """Test NotFound exception"""
    from uvicore.http.exceptions import NotFound
    exc = NotFound("Resource not found")
    assert exc is not None
    with pytest.raises(NotFound):
        raise NotFound("Test")
