import uvicore
from uvicore.http import Request, response
from uvicore.http.routing import WebRouter, Controller


@uvicore.controller()
class Features(Controller):
    """Features page.

    Demonstrates the app's custom Jinja processors (registered in the provider):
      * filter          {{ 'hello' | shout }}
      * context_filter  {{ 1234.5 | money }}
      * test            {% if n is prime %}
      * context_function {{ nav_active('app1.features') }}
    The numbers list is passed from the controller so the template can filter it.
    """

    def register(self, route: WebRouter):

        @route.get('/features', name='features')
        async def features(request: Request):
            return await response.View('app1/features.j2', {
                'request': request,
                'numbers': list(range(2, 24)),
                'price': 1299.9,
            })

        return route
