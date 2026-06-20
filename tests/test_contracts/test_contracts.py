import pytest
import uvicore
from uvicore.support.dumper import dump


@pytest.mark.asyncio
async def test_contracts_module_importable(app1):
    """Test that contracts module can be imported"""
    from uvicore import contracts
    assert contracts is not None


@pytest.mark.asyncio
async def test_user_info_contract_exists(app1):
    """Test that UserInfo contract interface exists"""
    from uvicore.contracts import UserInfo
    assert UserInfo is not None
