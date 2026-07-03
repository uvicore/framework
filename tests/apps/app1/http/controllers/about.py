import uvicore
from uvicore.http import Request, response
from uvicore.http.routing import WebRouter, Controller


@uvicore.controller()
class About(Controller):
    """About page.

    Demonstrates: an autoprefixed named route ('app1.about'), a second plain-text
    response on the same controller, and the Sidebar composer (registered for
    app1/about).
    """

    def register(self, route: WebRouter):

        @route.get('/about', name='about')
        async def about(request: Request):
            return await response.View('app1/about.j2', {
                'request': request,
            })

        # A non-HTML response - handy for smoke tests and to show response.Text
        @route.get('/about2', name='about2')
        async def about2():
            return response.Text('About2 plain text here')

        return route
