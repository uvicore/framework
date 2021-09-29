import os
import uvicore
from uvicore import log
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


@command()
@argument('name')
async def composer(name: str):
    """
    \b
    Generate a new web view composer schematic...
    \b
    USAGE:
        View Composers should be lower_understore and SINGULAR
    \b
        ./uvicore gen composer layout
        ./uvicore gen composer side_nav
    """
    stub = os.path.dirname(__file__) + '/stubs/composer.py'
    dest = uvicore.config('app.paths.view_composers') + '/' + name + '.py'

    Schematic(
        type='composer',
        stub=stub,
        dest=dest,
        replace = [
            ('xx_composername', name),
            ('xx_ComposerName', str.studly(name)),
        ]
    ).generate()

    # Get running package
    package = uvicore.app.package(main=True)

    log.nl()
    log.header('Add this to your Service Provider boot() or define_views()')
    print("self.composers('{}/*', '{}.http.composers.{}.{}')".format(package.short_name, package.name, name, str.studly(name)))
