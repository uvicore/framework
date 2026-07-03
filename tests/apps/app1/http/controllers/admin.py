import uvicore
from uvicore.contracts import UserInfo
from uvicore.http import Request, response
from uvicore.http.routing import WebRouter, Controller, Guard


@uvicore.controller()
class Admin(Controller):
    """Admin page (guarded).

    Registered inside a scopes=['authenticated'] group in routes/web.py, and the
    endpoint injects the current user via Guard().  The view dumps the UserInfo
    fields to demonstrate request.user + scope enforcement.
    """

    def register(self, route: WebRouter):

        @route.get('/admin', name='admin')
        async def admin(request: Request, user: UserInfo = Guard()):
            return await response.View('app1/admin.j2', {
                'request': request,
                'user': user,
            })

        return route
