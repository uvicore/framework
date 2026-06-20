import pytest
import uvicore
from uvicore.support.dumper import dump


@pytest.mark.asyncio
async def test_option_decorator_exists(app1):
    """Test that @option decorator works"""
    from uvicore.console import option
    assert callable(option), "@option decorator should be callable"


@pytest.mark.asyncio
async def test_group_decorator_works(app1):
    """Test @group decorator basic functionality"""
    from uvicore.console import group
    assert callable(group)
