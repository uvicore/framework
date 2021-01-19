# This is the main foundation config.  All items here can be overridden
# when used inside other applications.  Accessible at config('uvicore.foundation')

config = {

    # --------------------------------------------------------------------------
    # Registration Control
    # --------------------------------------------------------------------------
    # This lets you control the service provider registrations.  If this app
    # is used as a package inside another app you might not want some things
    # registered in that context.
    'registers': {
        'web_routes': False,
        'api_routes': False,
        'middleware': False,
        'views': False,
        'assets': False,
        'commands': True,
        'models': False,
        'tables': False,
        'seeders': False,
    }

}
