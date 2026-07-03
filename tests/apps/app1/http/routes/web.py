import uvicore
from uvicore.http.routing import Routes, WebRouter


@uvicore.routes()
class Web(Routes):
    """App1 web (server-rendered) routes.

    Routes and controllers are the same nested-router mechanism; a Routes class
    can carry class-level middleware/auth/scopes that apply to every child route.
    """

    # Class-level middleware/auth/scopes apply to all routes in this file, e.g.
    #middleware = [Guard()]
    #auth = Guard()

    def register(self, route: WebRouter):
        """Register Web route endpoints"""

        # Base module for string controller resolution (route.controller('home')
        # -> app1.http.controllers.home.Home)
        route.controllers = 'app1.http.controllers'

        # Public routes
        route.controller('home')
        route.controller('about')
        route.controller('features')
        route.controller('contact')
        route.controller('login')

        # Private routes - gated by the 'authenticated' scope (Guard)
        @route.group(scopes=['authenticated'])
        def private_routes():
            route.controller('admin')

        return route
