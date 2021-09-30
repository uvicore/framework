import uvicore
from uvicore.typing import Optional
from uvicore.support.dumper import dd, dump
from uvicore.http import Request, response
from uvicore.http.routing import WebRouter, Controller


@uvicore.controller()
class Login(Controller):

    def register(self, route: WebRouter):

        @route.get('/login', name='login')
        async def home(request: Request, referer: Optional[str] = None):
            user = request.user
            if not user.authenticated:
                from uvicore.http.exceptions import NotAuthenticated
                raise NotAuthenticated(headers={'WWW-Authenticate': 'Basic realm="App1 Web Realm"'})

            if referer:
                return response.Redirect(referer)
            return await response.View('app1/login.j2', {
                'request': request
            })

        @route.get('/logout', name='logout')
        async def home(request: Request):
            # Fixme.  I have request.authenticator (basic, session...)
            # and request.route_type (web or api)
            # I should make an auth.logout() method that handles each authenticator logout

            user = request.user
            if user.authenticated:
                from uvicore.http.exceptions import NotAuthenticated
                raise NotAuthenticated(headers={'WWW-Authenticate': 'Basic realm="App1 Web Realm"'})
            return response.HTML('Logged Out')

        # Return router
        return route
