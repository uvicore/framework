import click
import typer
from click_help_colors import HelpColorsCommand, HelpColorsGroup

group_kargs = {
    #'context_settings': dict(help_option_names=['-h', '--help']),
    'cls': HelpColorsGroup,
    'help_headers_color': 'yellow',
    'help_options_color': 'green',
}

cmd_kargs = {
    #'context_settings': dict(help_option_names=['-h', '--help']),
    'cls': HelpColorsCommand,
    'help_headers_color': 'yellow',
    'help_options_color': 'green',
}
