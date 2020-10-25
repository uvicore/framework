import uvicore
from uvicore.console import command
from uvicore.support.dumper import dd, dump


@command()
async def cli():
    """Interactive iPython Shell"""

    # from traitlets.config import Config
    # c = Config()

    # import IPython
    # IPython.start_ipython(config=c)



    import IPython
    from IPython.terminal.ipapp import load_default_config
    from traitlets.config.loader import Config


    # Get config from .env or somewhere, or load defaults
    config = load_default_config()

    config.TerminalInteractiveShell.banner1 = "banner 1 here"


    import sys
    print(sys.path)

    IPython.start_ipython(config=config)
