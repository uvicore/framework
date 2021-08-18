import uvicore
from uvicore.http import Request
from uvicore.http.routing import ApiRouter, Controller

# Extra
from uvicore.auth import UserInfo
from uvicore.http.routing import Guard
from uvicore.http.exceptions import HTTPException
from uvicore.http.params import Path, Query, Header, Cookie, Body, Form, File, Depends, Security


# ------------------------------------------------------------------------------
# Uvicore Controller Schematic
# This schematic is filled with examples, a suppliment to the docs.
# Pick the best example for your use case and modify as needed!
# ------------------------------------------------------------------------------


@uvicore.controller()
class xx_ControllerName(Controller):

    # --------------------------------------------------------------------------
    # Example:  Multiple ways to apply route level middleware including
    # auth guards with scoped permissions to this entire controller.
    # Tip: Your routes/api.py and routes/web.py are actually the same
    # as controllers.  In fact controllers are just nested routers.  So all
    # notes here also apply to your routes/* files.
    # --------------------------------------------------------------------------
    # Apply scopes to all routes and children controllers - simple and preferred
    #scopes = ['authenticated', 'employee']

    # Scopes is a shortcut to
    #auth = Guard(['authenticated', 'gardner'])

    # scopes and auth are shortcuts to the full middleware stack
    # middleware = [
    #     Guard(['authenticated', 'post_manager'])
    # ]

    # Optionally, apply scopes and also grab the current user
    # user: UserInfo = Guard(['authenticated'])
    #   Then in your routes, inject the user with
    #   async def welcome(request: Request, user: UserInfo = self.user):


    def register(self, route: ApiRouter):

        @route.get('/welcome', tags=['Welcome'])
        async def welcome():
            return {'welcome': 'to uvicore API!'}

        # @route.get('/posts', tags=['Post'])
        # async def posts() -> List[Post]:
        #     return await Post.query().get()

        # @route.get('/post/{id}', tags=['Post'])
        # async def post(id: int) -> Post:

        # Return router
        return route
