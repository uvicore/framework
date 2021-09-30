import uvicore
from uvicore.support.dumper import dd, dump
from uvicore.http import Request, response
from uvicore.http.routing import WebRouter, Controller
from fastapi import Depends

@uvicore.controller()
class About(Controller):

    def register(self, route: WebRouter):

        @route.get('/about', name='about')
        async def about(request: Request):
            return await response.View('app1/about.j2', {
                'request': request
            })

        @route.get('/about2')
        async def about2():
            return response.Text('About2 text here')

        # Return router
        return route
