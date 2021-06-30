# If using installed version of asyncclick
#import asyncclick as click

# If using local copy of asyncclick
from . import asyncclick as click

from .click_colors import HelpColorsCommand, HelpColorsGroup


def group(name=None, **attrs):
    defaults = {
        'cls': HelpColorsGroup,
        'help_headers_color': 'yellow',
        'help_options_color': 'green',
    }
    kwargs = {**defaults, **attrs}
    return click.group(name=name, **kwargs)


def command(name=None, cls=None, **attrs):
    # Click cmd kargs to add colored output
    defaults = {
        'cls': HelpColorsCommand,
        'help_headers_color': 'yellow',
        'help_options_color': 'green',
    }
    kwargs = {**defaults, **attrs}
    return click.command(name=name, **kwargs)
