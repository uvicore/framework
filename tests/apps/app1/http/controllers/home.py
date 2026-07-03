import uvicore
from uvicore.http import Request, response
from uvicore.http.routing import WebRouter, Controller


@uvicore.controller()
class Home(Controller):
    """Home page.

    Demonstrates: a named web route (kept as the un-prefixed name 'home' via
    autoprefix=False), rendering a Jinja view with response.View(), the Layout +
    Sidebar view composers, and template inheritance.
    """

    def register(self, route: WebRouter):

        @route.get('/', name='home', autoprefix=False)
        async def home(request: Request):
            return await response.View('app1/home.j2', {
                'request': request,
            })

        return route
