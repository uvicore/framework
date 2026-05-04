import pytest
import uvicore
from uvicore.support.dumper import dump


@pytest.mark.asyncio
async def test_composer_decorator_exists(app1):
    """Test @composer decorator"""
    from uvicore.foundation.decorators import composer
    assert callable(composer)


@pytest.mark.asyncio
async def test_job_decorator_exists(app1):
    """Test @job decorator"""
    from uvicore.foundation.decorators import job
    assert callable(job)


@pytest.mark.asyncio
async def test_event_decorator_exists(app1):
    """Test @event decorator"""
    from uvicore.foundation.decorators import event
    assert callable(event)


@pytest.mark.asyncio
async def test_model_decorator_exists(app1):
    """Test @model decorator"""
    from uvicore.foundation.decorators import model
    assert callable(model)


@pytest.mark.asyncio
async def test_provider_decorator_exists(app1):
    """Test @provider decorator"""
    from uvicore.foundation.decorators import provider
    assert callable(provider)
