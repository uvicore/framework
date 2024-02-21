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

    # Get calling package (main running app)
    package = uvicore.app.package(main=True)

    # Get stub (src)
    stub = os.path.dirname(__file__) + '/stubs/table.py'

    # Get destination for this filetype, considering the packages path customizations
    dest = package.folder_path('tables') + '/' + name + '.py'

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
@argument('tablename')
@argument('modelname')
async def seeder(tablename: str, modelname: str):
    """
    \b
    Generate a new Database table seeder schematic...
    \b
    USAGE:
        Seeder should match the lower_underscore PLURAL tablename and lower_understore SINGLUAR model name
    \b
        ./uvicore gen seeder users user
        ./uvicore gen seeder user_details user_detail
        ./uvicore gen seeder posts post
        ./uvicore gen seeder post_tags post_tag
    """

    # Get calling package (main running app)
    package = uvicore.app.package(main=True)

    # Get stub (src)
    stub = os.path.dirname(__file__) + '/stubs/seeder.py'

    # Get destination for this filetype, considering the packages path customizations
    dest = package.folder_path('seeders') + '/' + tablename + '.py'

    Schematic(
        type='seeder',
        stub=stub,
        dest=dest,
        replace = [
            ('xx_tablename', tablename),
            ('xx_TableName', str.studly(tablename)),
            ('xx_modelname', modelname),
            ('xx_ModelName', str.studly(modelname)),
        ]
    ).generate()

    uvicore.log.nl()
    uvicore.log.notice('Be sure to add this seeder to your ./database/seeders/__init__.py')

