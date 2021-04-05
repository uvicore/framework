import uvicore
from uvicore.console import click, group
from uvicore.console.events import command as ConsoleEvents


title_ideas = """
    A Fast Async Python Framework for CLI, Web and API

    High Performance Web, API and CLI Python Framework

    Python async Web, API and CLI fullstack Framework

    Fullstack Asynchronous Python Framework
    Python web framework
    Python Fullstack Asynchronous Web, API and CLI Framework

    Asynchronous Python Web, API and CLI Fullstack Framework

    The Async Python Framework for Craftsmen
    The Async Python Framework for Artisans
    The Artisanal Asynchronous Python Framework
"""

# Must include actual bind name when stacking decorators as it cannot deduce on its own.
# Bind decorator must come first in the stack
@uvicore.service('uvicore.console.console.cli', aliases=['Console', 'console', 'cli'])
@group(help=f"""
    \b
    Uvicore {uvicore.__version__}
    The Async Python Framework for Artisans.
    An Elegant Fullstack Python Web, API and CLI Framework

    Copyright (c) 2020 Matthew Reschke
    License http://mreschke.com/license/mit
""")
@click.version_option(version=uvicore.__version__, prog_name='Uvicore Framework', flag_value='--d')
async def cli():
    await console_startup()


async def console_startup():
    # FIXME, right here you can perform BEFORE any command code, like before_command event dispatch
    # Could also do this in the command decorator?  No because all commands are loaded up front, so all fire
    # before a single command does
    #print('before command here')
    #await uvicore.events.dispatch_async('cli_startup')
    await ConsoleEvents.Startup().codispatch()


@cli.resultcallback()
async def console_shutdown(result, **kwargs):
    # FIXME, right here you can perform AFTER any command code, like after_command event dispatch

    # Disconnect database
    # Will fail if uvicore.database package is not loaded, so check first
    if 'uvicore.database' in uvicore.app.providers:
        try:
            await uvicore.db.disconnect_all()
        except:
            pass

    #await uvicore.events.dispatch_async('cli_shutdown')
    await ConsoleEvents.Shutdown().codispatch()
# IoC Class Instance
# No because not to be used by the public
