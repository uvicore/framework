import logging
import sys

import prettyprinter

import uvicore

# Enable extras like @dataclass
prettyprinter.install_extras(exclude=[
     # Not using django, no need to print django models
    'django',

    # Maybe when I get a shell ?
    'ipython_repr_pretty',
    'ipython',
    'attrs',
])


def dump(*args):
    """Dump variables using prettyprinter"""

    # Detect if running in pytest
    if "pytest" in sys.modules: level = None

    for arg in args:
        if type(arg) == str:
            # I don't want string printed with dump because it adds quotes to the string
            # which seems confusing at times.
            #prettyprinter.cpprint(arg, width=10000, ribbon_width=10000)
            print(arg)
        else:
            width = 120
            if uvicore.config:
                if uvicore.config.app.dump.width:
                    width = uvicore.config.app.dump.width
            prettyprinter.cpprint(arg, width=width, ribbon_width=width)


def log_dump(*args):
    """Dump variables using prettyprinter and obey log levels.

    Only dump if log level INFO or DEBUG.
    Used from uvicore logger log.dump()"""

    # Get current log level of Console logger
    # Uvicore may not be loaded yet, if not, set default level to INFO
    level = None
    if uvicore.log: level = logging.getLevelName(uvicore.log.console_handler.level)

    # Detect if running in pytest
    if "pytest" in sys.modules: level = None

    # Only dump if Console log level is DEBUG or INFO
    if level == 'INFO' or level == 'DEBUG' or level is None:
        dump(*args)


def dd(*args):
    """Dump variables using prettyprinter and exit()"""
    dump(*args)
    exit()
