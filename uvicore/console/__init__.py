import uvicore
from uvicore.support.click import click, group_kargs


@click.group(**group_kargs, help=f"""
    \b
    Uvicore {uvicore.__version__}
    A Fast Async ASGI Python Framework for CLI, Web and API
    Copyright (c) 2020 Matthew Reschke
    License http://mreschke.com/license/mit
""")
@click.version_option(version=uvicore.__version__, prog_name='Uvicore Framework', flag_value='--d')
def cli():
    pass


# Public API for import * and doc gens
__all__ = ['cli']



# cli = typer.Typer(
#     cls=HelpColorsGroup,
#     help_headers_color='yellow',
#     help_options_color='green',
#     help="""\b
# Uvicore Python Framework
# Copyright (c) 2020 Matthew Reschke
# License MIT
# """)

# import click


# #@click.group(**group_kargs)
# @click.group()
# def cli():
#     """
#     \b
#     mRcore Python Framework for CLI, Web and API
#     Copyright (c) 2020 Matthew Reschke
#     License http://mreschke.com/license/mit
#     """
#     pass
