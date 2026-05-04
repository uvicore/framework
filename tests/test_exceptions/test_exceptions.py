import pytest
import uvicore
from uvicore.support.dumper import dump


@pytest.mark.asyncio
async def test_smart_exception_exists(app1):
    """Test that SmartException class exists"""
    from uvicore.exceptions import SmartException
    assert SmartException is not None


@pytest.mark.asyncio
async def test_smart_exception_can_be_raised(app1):
    """Test that SmartException can be raised"""
    from uvicore.exceptions import SmartException
    with pytest.raises(SmartException):
        raise SmartException("Test exception")


@pytest.mark.asyncio
async def test_exceptions_module_importable(app1):
    """Test that exceptions module can be imported"""
    from uvicore import exceptions
    assert exceptions is not None
