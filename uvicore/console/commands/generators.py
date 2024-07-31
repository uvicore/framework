import os
import uvicore
from uvicore import log
from uvicore.support import str
from uvicore.console import command, argument
from uvicore.support.dumper import dump, dd
from uvicore.support.schematic import Schematic


@command()
@argument('name')
async def command(name: str):
    """
    \b
    Generate a new CLI command schematic...
    \b
    USAGE:
        Commands should be lower_underscore and SINGULAR (plural is OK)
        Remember to manually add the command to your service provider!
    \b
        ./uvicore gen command welcome
        ./uvicore gen command process
        ./uvicore gen command scan_files
    """

    # Get calling package (main running app)
    package = uvicore.app.package(main=True)

    # Get stub (src)
    stub = os.path.dirname(__file__) + '/stubs/command.py'

    # Get destination for this filetype, considering the packages path customizations
    dest = package.folder_path('commands') + '/' + name + '.py'

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
    log.header('Add this to your Service Provider boot() or define_commands self.commands()')
    print("'{}': '{}.commands.{}.cli',".format(str.kebab(name), package.name, name))

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
        str.kebab(name),
        package.name,
        name,
    ))
