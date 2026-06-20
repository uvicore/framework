import pytest
import uvicore
from uvicore.support.dumper import dump


@pytest.mark.asyncio
async def test_foundation_module_importable(app1):
    """Test that foundation module can be imported"""
    from uvicore import foundation
    assert foundation is not None


@pytest.mark.asyncio
async def test_application_class_exists(app1):
    """Test that Application class exists"""
    from uvicore.foundation.application import Application
    assert Application is not None
