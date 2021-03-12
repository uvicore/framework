import uvicore
from uvicore.support.dumper import dd, dump
from uvicore.auth.middleware.auth import Guard
from uvicore.auth import User
from uvicore.http import Request, response
from uvicore.http.routing import WebRouter, Controller
from fastapi import Depends

@uvicore.controller()
class Admin(Controller):

    # Route middleware
    #middleware = [Guard()]
    #auth = Guard(guard='web')

    def register(self, route: WebRouter):

        #@route.get('/admin', name='admin', auth=Guard(['scope2']))
        #@route.get('/admin', name='admin', auth=Guard(['scope2'], guard='web'))
        #@route.get('/admin', name='admin', auth=Guard())
        @route.get('/admin', name='admin')
        #def home(request: Request, user: User = Guard()):
        def home(request: Request):
            #return user.email
            return response.View('app1/admin.j2', {
                'request': request
            })

        # Return router
        return route
