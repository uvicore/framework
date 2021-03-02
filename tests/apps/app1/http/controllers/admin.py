import uvicore
from uvicore.support.dumper import dd, dump
from uvicore.auth.middleware.auth import Guard
from uvicore.auth.models import User
from uvicore.http import Request, response
from uvicore.http.routing import WebRouter, Controller
from fastapi import Depends

@uvicore.controller()
class Admin(Controller):

    #user: User = Guard(['scope1'], guard='web')
    #user: User = Guard(['scope1'])
    #user: User = Guard(guard='web')

    def register(self, route: WebRouter):

        #@route.get('/admin', name='admin', auth=Guard(['scope2']))
        #@route.get('/admin', name='admin', auth=Guard(['scope2'], guard='web'))
        #@route.get('/admin', name='admin', auth=Guard())
        @route.get('/admin', name='admin')
        def home(request: Request):
            return response.View('app1/admin.j2', {
                'request': request
            })

        # Return router
        return route
