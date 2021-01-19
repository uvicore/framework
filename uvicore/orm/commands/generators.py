import os
import uvicore
from uvicore.support import str
from uvicore.support.dumper import dump, dd
from uvicore.support.schematic import Schematic
from uvicore.console import command, argument, option


@command()
@argument('name')
@argument('table')
async def model(name: str, table: str):
    """Generate a new ORM model schematic"""

    stub = os.path.dirname(__file__) + '/stubs/model.py'
    dest = uvicore.config('app.paths.models') + '/' + name + '.py'

    Schematic(
        type='model',
        stub=stub,
        dest=dest,
        replace = [
            ('xx_modelname', name),
            ('xx_ModelName', str.studly(name)),
            ('xx_tablename', table),
            ('xx_TableName', str.studly(table)),
        ]
    ).generate()
