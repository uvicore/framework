import pytest
import uvicore
from uvicore.support.dumper import dump


@pytest.mark.asyncio
async def test_asyncclick_main_imports(app1):
    """Test asyncclick imports"""
    from uvicore.console.asyncclick import command, group, argument, option
    assert callable(command)
    assert callable(group)
    assert callable(argument)
    assert callable(option)


@pytest.mark.asyncio
async def test_asyncclick_testing(app1):
    """Test asyncclick testing utilities"""
    from uvicore.console.asyncclick.testing import CliRunner
    assert CliRunner is not None


@pytest.mark.asyncio
async def test_command_parser(app1):
    """Test command parsing"""
    from uvicore.console.asyncclick import command, argument

    @command()
    @argument('name')
    async def test_cmd(name):
        return name

    assert callable(test_cmd)


@pytest.mark.asyncio
async def test_option_parser(app1):
    """Test option parsing"""
    from uvicore.console.asyncclick import command, option

    @command()
    @option('--verbose', is_flag=True)
    async def test_cmd(verbose):
        return verbose

    assert callable(test_cmd)


@pytest.mark.asyncio
async def test_group_creation(app1):
    """Test group creation"""
    from uvicore.console.asyncclick import group, command

    @group()
    async def test_group():
        pass

    @test_group.command()
    async def test_cmd():
        pass

    assert callable(test_group)
