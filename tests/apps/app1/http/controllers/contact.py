import uvicore
from uvicore.http import Request, response
from uvicore.http.request import Form
from uvicore.http.routing import WebRouter, Controller


@uvicore.controller()
class Contact(Controller):
    """Contact page.

    Demonstrates: an HTML form (GET) and form POST handling using FastAPI-style
    Form(...) parameters on a web route.  The POST re-renders the same view with
    a success alert echoing the submitted values.
    """

    def register(self, route: WebRouter):

        @route.get('/contact', name='contact')
        async def contact(request: Request):
            return await response.View('app1/contact.j2', {
                'request': request,
                'submitted': None,
            })

        @route.post('/contact', name='contact')
        async def contact_post(
            request: Request,
            name: str = Form(...),
            email: str = Form(...),
            message: str = Form(''),
        ):
            return await response.View('app1/contact.j2', {
                'request': request,
                'submitted': {'name': name, 'email': email, 'message': message},
            })

        return route
