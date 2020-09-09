import uvicore
from uvicore.configuration import Env
from uvicore.support import path

def application(is_console: bool = False) -> None:
    # Base path
    base_path = path.find_base(__file__) + '/testapp/app'

    # Load .env from environs
    #Env().read_env(base_path + '/.env')

    # Import this apps config (import must be after Env())
    from ..config.app import config as app_config

    # Bind bootstrap level IoC overrides
    uvicore.ioc.bind_map(app_config['ioc'])

    # Instantiate the Application into the uvicore.app instance
    uvicore.app = uvicore.ioc.make('Application')

    # Instantiate the Event system into the uvicore.events instance
    uvicore.events = uvicore.ioc.make('Dispatcher')

    # Bootstrap the Uvicore Application (Either CLI or HTTP entry points based on is_console)
    uvicore.app.bootstrap(app_config, base_path, is_console)

    # Return application
    return uvicore.app
