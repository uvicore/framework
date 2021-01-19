import os
import uvicore
from uvicore.support import str
from uvicore.support.dumper import dump, dd
from uvicore.support.schematic import Schematic
from uvicore.console import command, argument, option


@command()
@argument('name')
async def table(name: str):
    """Generate a new Database table schematic"""
    stub = os.path.dirname(__file__) + '/stubs/table.py'
    dest = uvicore.config('app.paths.tables') + '/' + name + '.py'

    Schematic(
        type='table',
        stub=stub,
        dest=dest,
        replace = [
            ('xx_tablename', name),
            ('xx_TableName', str.studly(name)),
        ]
    ).generate()


@command()
@argument('name')
async def seeder(name: str):
    """Generate a new Database table seeder schematic"""
    stub = os.path.dirname(__file__) + '/stubs/seeder.py'
    dest = uvicore.config('app.paths.seeders') + '/' + name + '.py'

    Schematic(
        type='seeder',
        stub=stub,
        dest=dest,
        replace = [
            ('xx_modelname', name),
            ('xx_ModelName', str.studly(name)),
        ]
    ).generate()
