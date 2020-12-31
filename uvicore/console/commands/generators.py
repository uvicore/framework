import uvicore
from uvicore.console import command
from uvicore.support.dumper import dump, dd

@command()
async def command():
    """Generate a new CLI Command"""
    print('make command')
