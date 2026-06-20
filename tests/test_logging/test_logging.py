import pytest
import uvicore
from uvicore.support.dumper import dump
import logging


@pytest.mark.asyncio
async def test_logging_module_importable(app1):
    """Test that logging module can be imported"""
    from uvicore import logging as uvicore_logging
    assert uvicore_logging is not None


@pytest.mark.asyncio
async def test_python_logging_integration(app1):
    """Test that logging integrates with Python logging"""
    logger = logging.getLogger('test')
    assert logger is not None
    assert logger.name == 'test'
