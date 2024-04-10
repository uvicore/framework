import uvicore
from uvicore.http import Request, response
from uvicore.http.routing import WebRouter, Controller

# Extra
# from uvicore.auth import UserInfo
# from uvicore.http.routing import Guard
# from uvicore.typing import Dict, List, Optional
# from uvicore.http.exceptions import HTTPException
# from uvicore.http.params import Path, Query, Header, Cookie, Body, Form, File, Depends, Security


# ------------------------------------------------------------------------------
# Uvicore Controller Schematic
# This schematic is filled with examples, a suppliment to the docs.
# Pick the best example for your use case and modify as needed!
# ------------------------------------------------------------------------------


@uvicore.controller()
class xx_ControllerName(Controller):

    # --------------------------------------------------------------------------
    # Example:  Multiple ways to apply route level middleware including
    # auth guards with scoped permissions to this entire controller.
    # Tip: Your routes/api.py and routes/web.py are actually the same
    # as controllers.  In fact controllers are just nested routers.  So all
    # notes here also apply to your routes/* files and controllers.
    # --------------------------------------------------------------------------
    # Apply scopes to all routes and children controllers - simple and preferred
    #scopes = ['authenticated', 'employee']

    # Scopes is a shortcut to
    #auth = Guard(['authenticated'])

    # Scopes and auth are shortcuts to the full middleware stack
    # middleware = [
    #     Guard(['authenticated']),
    #     Any other route based middleware here
    # ]

    # Optionally, apply scopes and also grab the current user
    # user: UserInfo = Guard(['authenticated'])
    #   Then in your routes, inject the user with
    #   async def welcome(request: Request, user: UserInfo = self.user):

    def register(self, route: WebRouter):
        """Register Web Controller Endpoints"""

        # ----------------------------------------------------------------------
        # Example: Basic route responding with a view template
        # ----------------------------------------------------------------------
        # @route.get('/example1/{id}')
        # async def example1(request: Request, id: int):
        #     # Template should be in http/views/xx_appname/template.j2
        #     # All web routes require request: Request
        #     # All template views require the request be piped through
        #     # To see all route details run ./uvicore package list
        #     return await response.View('xx_appname/template.j2', {
        #         'request': request,
        #         'id': id,
        #     })


        # ----------------------------------------------------------------------
        # Example: Other types of responses
        # ----------------------------------------------------------------------
        # @route.get('/example2')
        # async def example2(request: Request):
        #     return response.Text('Text Here')
        #     return response.HTML('<b>HTML</b> here')
        #     return response.JSON({'json':'here'})
        #     return response.UJSON({'json':'here'}) # requires ujson dependency
        #     return response.ORJSON({'json':'here'}) # requires orjson dependency
        #     # and more ... see uvicore/http/response.py


        # ----------------------------------------------------------------------
        # Example: GET request variables
        # curl http://localhost/?name=asdf
        # ----------------------------------------------------------------------
        # @route.get('/example2')
        # async def example2(request: Request, name: str):
        #     return response.Text(name)


        # ----------------------------------------------------------------------
        # Example: Changing the route name
        # Each route is given a name automatically.  A name is what you can use
        # to reference the route in your code and view templates.  Try to use the
        # route name instead of the path as paths WILL change as other users use
        # your library because they can tweak the BASE PATH.  Views should be using
        # {{ url('xx_appname.ex2a')}}, never /example2a
        # If you don't specify a name, uvicore makes a name automatically
        # from the path, even nested paths from groups.  Name always starts
        # with your apps name, ie: xx_appname.
        # ----------------------------------------------------------------------
        # @route.get('/example2a', name='ex2a')
        # async def example2a(request: Request):
        #     # Route name is xx_appname.ex2a
        #     return response.Text('example2a')


        # ----------------------------------------------------------------------
        # Example: Override the naming autoprefix
        # When you define a custom route name, a prefix of xx_appname. is
        # automatically added keeping your route scoped to this package.
        # In order to set a full name you must set autoprefix=False.
        # This is handy when you want to override a route from another package.
        # ----------------------------------------------------------------------
        # @route.get('/example2b', name='someother.app.ex2b', autoprefix=False)
        # async def example2b(request: Request):
        #     # Route name is someother.app.ex2b
        #     return response.Text('example2b')


        # ----------------------------------------------------------------------
        # Example: Injecting the current User using the Guard dependency
        # ----------------------------------------------------------------------
        # @route.get('/example3')
        # async def example3(request: Request, user: UserInfo = Guard()):
        #     dump(user)
        #     return response.Text('example3')


        # ----------------------------------------------------------------------
        # Example: Injecting the current User using the Guard dependency
        # And guarding the route based on the users permissions (scopes)
        # Benifit of this vs decorator scopes is you also get the current User
        # injected so you don't have to use request.scope['user]
        # curl -u user:pass http://localhost/example4
        # ----------------------------------------------------------------------
        # @route.get('/example4')
        # async def example4(request: Request, user: UserInfo = Guard(['authenticated'])):
        #     dump(user);
        #     return response.Text('example4')


        # ----------------------------------------------------------------------
        # Example: Getting the user from request.scope['user']
        # And guarding the route from the decorator using the scopes shortcut
        # curl -u user:pass http://localhost/example5
        # ----------------------------------------------------------------------
        # @route.get('/example5', scopes=['authenticated'])
        # async def example5(request: Request):
        #     user: UserInfo = request.scope['user'];
        #     dump(user)
        #     return response.Text('example5')


        # ----------------------------------------------------------------------
        # Example: Using the auth guard instead of scopes shortcut
        # while also getting the current user from request.scope['user']
        # curl -u user:pass http://localhost/example5a
        # ----------------------------------------------------------------------
        # @route.get('/example5a', auth=Guard(['authenticated']))
        # async def example5a(request: Request):
        #     user: UserInfo = request.scope['user'];
        #     dump(user)
        #     return response.Text('example5a')


        # ----------------------------------------------------------------------
        # Example: Using the per route middleware instead of auth or scopes
        # curl -u user:pass http://localhost/example5b
        # ----------------------------------------------------------------------
        # @route.get('/example5b', middleware=[
        #     Guard(['authenticated'])
        # ])
        # async def example5b(request: Request):
        #     user: UserInfo = request.scope['user'];
        #     dump(user)
        #     return response.Text('example5b')


        # ----------------------------------------------------------------------
        # Example: POST with form body
        # curl -X POST -F 'name=matthew' http://localhost/
        # http -v --form POST http://localhost/ name=matthew
        # ----------------------------------------------------------------------
        # @route.post('/example6')
        # async def example6(request: Request, name: str = Form(...)):
        #     return response.Text(name)


        # ----------------------------------------------------------------------
        # Example raise proper HTTP Exception
        # ----------------------------------------------------------------------
        # @route.get('/example7')
        # async def example7(request: Request):
        #     raise HTTPException(404, 'bad stuff')


        # ----------------------------------------------------------------------
        # Example: Grouping routes for common paths and scopes
        # Routes will be /group1/example8 and /group1/subgroup1/example9
        # with scopped permissions on both routes.
        # IF you also set name='g1', all route names will be
        # xx_appname.g1.example8 instead of autonamed xx_appname.group1.example8
        # ----------------------------------------------------------------------
        # @route.group('/group1', scopes=['authenticated'])
        # def group1():
        #     @route.get('/example8')
        #     async def example8(request: Request):
        #         return response.Text("example8")

        #     @route.group('/subgroup1')
        #     def subgroup1():
        #         @route.get('/example9')
        #         async def example9(request: Request):
        #             return response.Text("example9")


        # ----------------------------------------------------------------------
        # Example: Routes as method callbacks (no decorators)
        # ----------------------------------------------------------------------
        # def example10(request: Request):
        #     return response.Text('example10')
        # route.get('/example10', example10)


        # ----------------------------------------------------------------------
        # Example: Groups and routes as method callbacks (no decorators)
        # ----------------------------------------------------------------------
        # def example11(request: Request):
        #     return response.Text('example11')
        # def example12(request: Request):
        #     return response.Text('example12')
        # route.group('/group2', scopes=['authenticated'], routes=[
        #     route.get('/example11', example11),
        #     route.get('/example12', example12),
        # ])


        # ----------------------------------------------------------------------
        # Example: Including other route files and controllers
        # Technically, there is no difference between your routes files
        # in http/routes/web.py and http/routes/api.py and your controllers
        # or api controllers.  They are all just one huge nested router.
        # They are only split up for logical convenience.  Just as you included
        # controlers from your http/routes/web.py, you can also include other
        # routes here.
        # ----------------------------------------------------------------------
        # route.controller('xx_vendor.xx_appname.http.controllers.some.other.Other')

        # Also, route.controller and route.include are aliases of each other, same thing.
        # route.include('xx_vendor.xx_appname.http.controllers.some.other2.Other2')

        # Instead of typing the full module path, if route.controllers is defined
        # Then all .controller() and .include() can use relative paths
        # route.controllers = 'xx_vendor.xx_appname.http.controllers'

        # Looks for Class in xx_vendor.xx_appname.http.controllers.some.Some
        # route.controller('some')

        # Leading period means APPEND path to defined route.controllers
        # So this looks for xx_vendor.xx_appname.http.controllers.other3.Other3
        # route.controller('.other3.Other3')

        # If no leading . but other . exists, then it is assuming a full path,
        # regardless if route.controllers is defined or not.


        # Return router
        # Must always return the router at the end of every controller and routes file
        # as this is one infinitely recursive nested router configuration.
        return route
