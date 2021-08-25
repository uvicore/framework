import os
import uvicore
from uvicore.support import str
from uvicore.support.dumper import dump, dd
from uvicore.support.schematic import Schematic
from uvicore.console import command, argument, option


@command()
@argument('name')
async def controller(name: str):
    """
    \b
    Generate a new HTTP Web controller schematic...
    \b
    USAGE:
        Web Controllers should be lower_understore and SINGULAR
    \b
        ./uvicore gen controller home
        ./uvicore gen controller about
        ./uvicore gen controller contact_us
    """
    stub = os.path.dirname(__file__) + '/stubs/controller.py'
    dest = uvicore.config('app.paths.controllers') + '/' + name + '.py'

    Schematic(
        type='controller',
        stub=stub,
        dest=dest,
        replace = [
            ('xx_controllername', name),
            ('xx_ControllerName', str.studly(name)),
        ]
    ).generate()


@command()
@argument('name')
async def api_controller(name: str):
    """
    \b
    Generate a new HTTP API controller schematic...
    \b
    USAGE:
        API Controllers should be lower_understore and SINGULAR
    \b
        ./uvicore gen controller user
        ./uvicore gen controller user_detail
        ./uvicore gen controller post
        ./uvicore gen controller post_tag
    """
    stub = os.path.dirname(__file__) + '/stubs/api_controller.py'
    dest = uvicore.config('app.paths.api') + '/' + name + '.py'

    Schematic(
        type='api_controller',
        stub=stub,
        dest=dest,
        replace = [
            ('xx_controllername', name),
            ('xx_ControllerName', str.studly(name)),
        ]
    ).generate()
