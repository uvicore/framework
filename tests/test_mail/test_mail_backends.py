import pytest
import uvicore
from uvicore.support.dumper import dump


@pytest.mark.asyncio
async def test_mail_module_exists(app1):
    """Test mail module"""
    from uvicore import mail as mail_mod
    assert mail_mod is not None


@pytest.mark.asyncio
async def test_mail_service_available(app1):
    """Test mail service in IoC container"""
    from uvicore.mail import Mail
    mail = Mail()
    assert mail is not None
