import os
import uvicore
from uvicore.support import str
from uvicore.support.dumper import dump, dd
from uvicore.support.schematic import Schematic
from uvicore.console import command, argument, option


@command()
@argument('name')
async def table(name: str):
    """
    \b
    Generate a new Database table schematic...
    \b
    USAGE:
        Tables should be lower_underscore and PLURAL
        If a table is awkward as plural, ok to make a few singluar (user_info)
    \b
        ./uvicore gen table users
        ./uvicore gen table user_details
        ./uvicore gen table posts
        ./uvicore gen table post_tags
    """
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

    uvicore.log.nl()
    uvicore.log.notice('Be sure to add this table to your ./database/tables/__init__.py')


@command()
@argument('name')
async def seeder(name: str):
    """
    \b
    Generate a new Database table seeder schematic...
    \b
    USAGE:
        Seeder should match the lower_underscore PLURAL tablenames
    \b
        ./uvicore gen seeder users
        ./uvicore gen seeder user_details
        ./uvicore gen seeder posts
        ./uvicore gen seeder post_tags
    """
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

    uvicore.log.nl()
    uvicore.log.notice('Be sure to add this seeder to your ./database/seeders/__init__.py')

