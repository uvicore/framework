import os
import uvicore
from uvicore.support import str
from uvicore import log
from uvicore.console import command, argument
from uvicore.support.dumper import dump, dd
from uvicore.support.schematic import Schematic


@command()
@argument('name')
async def command(name: str):
    """Generate a new CLI Command"""

    stub = os.path.dirname(__file__) + '/stubs/command.py'
    dest = uvicore.config('app.paths.commands') + '/' + name + '.py'

    Schematic(
        type='command',
        stub=stub,
        dest=dest,
        replace = [
            ('xx_name', name)
        ]
    ).generate()

    # Get running package
    package = uvicore.app.package(main=True)

    log.nl()
    log.header('Add this to your Service Provider commands List')
    print("'{}': '{}.commands.{}.cli',".format(name, package.name, name))

    log.nl()
    log.notice('IF you do NOT have a self.commands() already in your Service Provider, add this')
    print("""self.commands(
    group='{}',
    help='{} Commands',
    commands={{
        '{}': '{}.commands.{}.cli',
    }}
)""".format(
        package.short_name,
        str.studly(package.short_name),
        name,
        package.name,
        name,
    ))
