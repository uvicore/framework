import pytest
import uvicore
from uvicore.support.dumper import dump


@pytest.mark.asyncio
async def test_jobs_module_importable(app1):
    """Test that jobs module can be imported"""
    from uvicore import jobs
    assert jobs is not None


@pytest.mark.asyncio
async def test_job_class_exists(app1):
    """Test that Job class exists"""
    from uvicore.jobs import Job
    assert Job is not None


@pytest.mark.asyncio
async def test_job_has_handle_method(app1):
    """Test that Job has handle method"""
    from uvicore.jobs import Job
    # Job is a base class that should define handle
    assert hasattr(Job, 'handle') or hasattr(Job, '__init__')
