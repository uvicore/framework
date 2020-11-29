import uvicore
from uvicore.console import click, group


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
@uvicore.service('uvicore.console.console._cli', aliases=['Console', 'console', 'cli'])
@group(help=f"""
    \b
    Uvicore {uvicore.__version__}
    The Async Python Framework for Artisans.
    An Elegant Fullstack Python Web, API and CLI Framework

    Copyright (c) 2020 Matthew Reschke
    License http://mreschke.com/license/mit
""")
@click.version_option(version=uvicore.__version__, prog_name='Uvicore Framework', flag_value='--d')
def _cli():
    pass


# IoC Class Instance
# No because not to be used by the public
