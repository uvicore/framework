import uvicore
from uvicore.configuration import Env
from uvicore.support import path
from uvicore.support.dumper import dd, dump


def application(is_console: bool = False) -> None:
    """Bootstrap the application either from the CLI or Web entry points

    Bootstrap only runs when this package is running as the main app via
    ./uvicore or uvicorn/gunicorn server
    """

    # Base path
    base_path = path.find_base(__file__) + '/testapp/app'

    # Load .env from environs - NO, not for this test environment
    # NO - Env().read_env(base_path + '/.env')

    # Import this apps config (import must be after Env())
    from ..config.app import config as app_config

    # Bootstrap the Uvicore Application (Either CLI or HTTP entry points based on is_console)
    uvicore.bootstrap(app_config, base_path, is_console)

    # Return application
    return uvicore.app
