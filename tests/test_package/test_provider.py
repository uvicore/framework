import pytest
import uvicore
from uvicore.support.dumper import dump


@pytest.mark.asyncio
async def test_provider_class_exists(app1):
    """Test that Provider class exists"""
    from uvicore.package import Provider
    assert Provider is not None


@pytest.mark.asyncio
async def test_provider_decorator_exists(app1):
    """Test that @provider decorator exists"""
    from uvicore import provider
    assert callable(provider), "@provider decorator should be callable"


@pytest.mark.asyncio
async def test_provider_has_register_method(app1):
    """Test that Provider has register method"""
    from uvicore.package import Provider
    assert hasattr(Provider, 'register'), "Provider should have register method"


@pytest.mark.asyncio
async def test_provider_has_boot_method(app1):
    """Test that Provider has boot method"""
    from uvicore.package import Provider
    assert hasattr(Provider, 'boot'), "Provider should have boot method"
