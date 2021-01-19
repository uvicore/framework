import uvicore
from uvicore.console import command, argument, option
from uvicore.support.dumper import dump, dd


@command()
async def command():
    """A New CLI Command"""
    print('New command here')
