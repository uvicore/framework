import pytest
import uvicore
from uvicore.support.dumper import dump


@pytest.mark.asyncio
async def test_templating_module_importable(app1):
    """Test that templating module can be imported"""
    from uvicore import templating
    assert templating is not None


@pytest.mark.asyncio
async def test_jinja2_engine_available(app1):
    """Test that Jinja2 templating engine is available"""
    from uvicore.templating import engine
    assert engine is not None
