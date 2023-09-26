import uvicore
from uvicore.console import command, argument, option
from uvicore.support.dumper import dd, dump


@command()
def info():
    """Running Application Information"""
    uvicore.log.header("Final Merged Application Information")
    uvicore.log.line()

    dump(uvicore.app._running_config)

