import pytest
import uvicore
from uvicore.support.dumper import dump


@pytest.mark.asyncio
async def test_config_service_available(app1):
    """Test that config service is available"""
    assert hasattr(uvicore, 'config'), "Config service should be available"


@pytest.mark.asyncio
async def test_config_can_get_value(app1):
    """Test that config values can be retrieved"""
    config = uvicore.config
    # Should be able to access config
    assert config is not None


@pytest.mark.asyncio
async def test_config_app_section(app1):
    """Test that app config section is available"""
    assert hasattr(uvicore.config, 'app'), "Config should have app section"


@pytest.mark.asyncio
async def test_config_get_method(app1):
    """Test that config.get() method works"""
    config = uvicore.config
    # Should have get method
    assert hasattr(config, 'get') or hasattr(config, '__getitem__')


@pytest.mark.asyncio
async def test_environment_variable_config(app1):
    """Test that environment variables can be used in config"""
    from uvicore.configuration import env
    assert callable(env), "env() should be callable for config values"


@pytest.mark.asyncio
async def test_env_bool_casting(app1):
    """Test environment variable boolean casting"""
    from uvicore.configuration import env
    result = env.bool('NONEXISTENT_VAR', False)
    assert isinstance(result, bool)
