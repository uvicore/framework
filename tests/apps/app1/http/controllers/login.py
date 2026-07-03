import uvicore
from uvicore.http import Request, response
from uvicore.http.request import Form
from uvicore.http.routing import WebRouter, Controller


@uvicore.controller()
class Login(Controller):
    """Login / logout.

    Illustrative only - it renders a login form, accepts a form POST, and shows
    the current request.user auth state; it does not implement a real credential
    backend.  Logout demonstrates a redirect response back to the home route.
    """

    def register(self, route: WebRouter):

        @route.get('/login', name='login')
        async def login(request: Request):
            return await response.View('app1/login.j2', {
                'request': request,
                'user': request.user,
                'attempted': None,
            })

        @route.post('/login', name='login')
        async def login_post(request: Request, username: str = Form(...), password: str = Form('')):
            # Illustrative: no real credential check, just echo the attempt.
            return await response.View('app1/login.j2', {
                'request': request,
                'user': request.user,
                'attempted': username,
            })

        @route.get('/logout', name='logout')
        async def logout(request: Request):
            # Redirect helper (Starlette RedirectResponse) back to the home route
            return response.Redirect(str(request.url_for('home')))

        return route
