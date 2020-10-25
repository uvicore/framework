import uvicore
import logging
import prettyprinter

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

    # Get current log level of Console logger
    level = logging.getLevelName(uvicore.log.console_handler.level)

    # Only dump if Console log level is DEBUG or INFO
    if level == 'INFO' or level == 'DEBUG':
        for arg in args:
            if type(arg) == str:
                prettyprinter.cpprint(arg, width=10000, ribbon_width=10000)
            else:
                prettyprinter.cpprint(arg)


def dd(*args):
    """Dump variables using prettyprinter and exit()"""
    dump(*args)
    exit()
