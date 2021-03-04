import uvicore
from uvicore.console import command
from uvicore.support.dumper import dd, dump


@command()
async def cli():
    """Interactive iPython Shell"""


    # Example of how to manually get uvicore going
    """
    cd ~/Code/mreschke/python/uvicore/uvicore
    PYTHONPATH=./tests/apps ipython

    import uvicore
    from app1.services import bootstrap
    app = bootstrap.application(is_console=True)

    from uvicore.support.dumper import dump, dd
    from app1 import models

    dump( await models.Post.query().include('creator', 'comments', 'tags').find(1) )

    provider = uvicore.config.app.auth.providers.users
    dump( await models.User.userinfo(provider, username='manager1@example.com') )


    """
    #
    # ipython
    #


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
