import pytest
import uvicore
from uvicore.support.dumper import dump


@pytest.mark.asyncio
async def test_mail_module_importable(app1):
    """Test that mail module can be imported"""
    from uvicore import mail
    assert mail is not None


@pytest.mark.asyncio
async def test_mail_class_exists(app1):
    """Test that Mail class exists"""
    from uvicore.mail import Mail
    assert Mail is not None
