import sys
import uvicore
import logging
from uvicore.support.printer import prettyprinter


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


def dd(*args):
    """Dump variables using prettyprinter and exit()"""
    dump(*args)
    exit()
