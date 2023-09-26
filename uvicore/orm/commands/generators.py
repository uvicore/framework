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
    """
    \b
    Generate a new ORM model schematic...
    \b
    USAGE:
        Models should be lower_understore and SINGULAR
        While their table should be lower_understore and PLURAL
    \b
        ./uvicore gen model user users
        ./uvicore gen model user_detail user_details
        ./uvicore gen model post posts
        ./uvicore gen model post_tag post_tags
    """

    # Get calling package (main running app)
    package = uvicore.app.package(main=True)

    # Get stub (src)
    stub = os.path.dirname(__file__) + '/stubs/model.py'

    # Get destination for this filetype, considering the packages path customizations
    dest = package.folder_path('models') + '/' + name + '.py'

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

    uvicore.log.nl()
    uvicore.log.notice('Be sure to add this model to your ./models/__init__.py')
