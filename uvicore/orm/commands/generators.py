import uvicore
from uvicore.console import command
from uvicore.support.dumper import dump, dd

@command()
async def model():
    """Generate a new ORM model schematic"""
    print('make model')
