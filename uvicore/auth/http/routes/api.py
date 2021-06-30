import uvicore
from uvicore.http.routing import Routes, ApiRouter, ModelRouter


@uvicore.routes()
class Api(Routes):

    # Apply scopes to all routes and children controllers
    #scopes = ['authenticated']
    #scopes = ['authenticated', 'employee']
    #scopes = None

    def register(self, route: ApiRouter):
        """Register API Route Endpoints"""

        # Define controller base path
        route.controllers = 'uvicore.auth.http.api'

        @route.group(tags=['Auth'])
        def private_routes():

            @route.get('/auth/userinfo')
            def userinfo():
                return {'hi': 'there'}

        # Return router
        return route
