import pytest
import uvicore
from uvicore.support.dumper import dump


@pytest.mark.asyncio
async def test_server_module_importable(app1):
    """Test HTTP server module can be imported"""
    from uvicore.http import server
    assert server is not None


@pytest.mark.asyncio
async def test_decorators_controller_exists(app1):
    """Test @controller decorator"""
    from uvicore.foundation.decorators import controller
    assert callable(controller)


@pytest.mark.asyncio
async def test_controller_class_importable(app1):
    """Test Controller base class"""
    from uvicore.http.routing import Controller
    assert Controller is not None


@pytest.mark.asyncio
async def test_auto_api_class_exists(app1):
    """Test AutoApi functionality"""
    from uvicore.http.routing import AutoApi
    assert AutoApi is not None


@pytest.mark.asyncio
async def test_static_files_module(app1):
    """Test static file handling"""
    from uvicore.http import static
    assert static is not None
