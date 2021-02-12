import sys
import asyncclick as click
from asyncclick import argument, option
from .decorators import command, group

# Does work without error, but never accessed by a user, so no point
# No from .console import cli

# The console package uses a __init__.py because users will import these
# methods from their own commands and we want a nicer import which looks
# like - from uvicore.console import command


def command_is(command: str):
    command = command.lower()
    running = ' '.join(sys.argv[1:]).lower()
    #return len(sys.argv) > 1 and command.lower() == running.lower()
    return command in running
