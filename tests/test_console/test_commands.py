import pytest
import uvicore
from uvicore.console import command
from uvicore.support.dumper import dump
from click.testing import CliRunner


@pytest.mark.asyncio
async def test_console_module_importable(app1):
    """Test that console module can be imported"""
    from uvicore import console
    assert console is not None


@pytest.mark.asyncio
async def test_command_decorator_exists(app1):
    """Test that @command decorator works"""
    from uvicore.console import command
    assert callable(command), "@command decorator should be callable"


@pytest.mark.asyncio
async def test_group_decorator_exists(app1):
    """Test that @group decorator works"""
    from uvicore.console import group
    assert callable(group), "@group decorator should be callable"


@pytest.mark.asyncio
async def test_argument_decorator_exists(app1):
    """Test that @argument decorator works"""
    from uvicore.console import argument
    assert callable(argument), "@argument decorator should be callable"


@pytest.mark.asyncio
async def test_option_decorator_exists(app1):
    """Test that @option decorator works"""
    from uvicore.console import option
    assert callable(option), "@option decorator should be callable"


@pytest.mark.asyncio
async def test_command_is_utility_exists(app1):
    """Test that command_is() utility exists"""
    from uvicore.console import command_is
    assert callable(command_is), "command_is() utility should be callable"
