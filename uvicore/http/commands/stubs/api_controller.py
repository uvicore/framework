import uvicore
from uvicore.typing import Dict
from uvicore.http import Request
from uvicore.http.exceptions import HTTPException
from uvicore.http.routing import ApiRouter, Controller

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
    #auth = Guard(['authenticated', 'gardner'])

    # Scopes and auth are shortcuts to the full middleware stack
    # middleware = [
    #     Guard(['authenticated', 'post_manager']),
    #     Any other route based middleware here
    # ]

    # Optionally, apply scopes and also grab the current user
    # user: UserInfo = Guard(['authenticated'])
    #   Then in your routes, inject the user with
    #   async def welcome(request: Request, user: UserInfo = self.user):

    def register(self, route: ApiRouter):
        """Register API Controller Endpoints"""

        # ----------------------------------------------------------------------
        # Example: Basic route responding with a view dict to JSON blob
        # ----------------------------------------------------------------------
        @route.get('/example1', tags=['Examples'])
        async def example1() -> Dict:
            """This docstring shows up in openapi"""
            try:
                return {'welcome': 'to uvicore API!'}
            except Exception as e:
                raise HTTPException(500, exception=e)


        # ----------------------------------------------------------------------
        # Example: Route returning a Model schema with python return type hint
        # ----------------------------------------------------------------------
        # @route.get('/example2', tags=['Examples'])
        # async def example2()) -> List[models.Post]:
        #     """This docstring shows up in openapi"""
        #     return await models.Post.query().get()


        # ----------------------------------------------------------------------
        # Example: Route returning a Model schema using response_model
        # ----------------------------------------------------------------------
        # @route.get('/example3', response_model=List[models.Post], tags=['Examples'])
        # async def example3():
        #     return await models.Post.query().get()


        # ----------------------------------------------------------------------
        # Example: Auth guard using scopes shortcut
        # ----------------------------------------------------------------------
        # @route.get('/example4/{id}', scopes=['authenticated'], tags=['Examples'])
        # async def example4(id: int) -> models.Post:
        #     return await models.Post.query().find(id)


        # ----------------------------------------------------------------------
        # Example: Auth guard using auth shortcut
        # ----------------------------------------------------------------------
        # @route.get('/example5/{id}', auth=Guard(['authenticated']), tags=['Examples'])
        # async def example5(id: int) -> models.Post:
        #     return await models.Post.query().find(id)


        # ----------------------------------------------------------------------
        # Example: Auth guard while also getting the current user
        # Also accepts an optional GET parameter (?name=matthew)
        # ----------------------------------------------------------------------
        # @route.get('/example6/{id}', tags=['Examples'])
        # async def example6(id: int, name: Optional[str], user: UserInfo = Guard(['authenticated'])) -> models.Post:
        #     dump(name, user)
        #     return await models.Post.query().find(id)


        # ----------------------------------------------------------------------
        # Example: Auth guard using middleware
        # Get the current user with request.scope['user']
        # Also accepts an optional GET parameter (?name=matthew)
        # ----------------------------------------------------------------------
        # @route.get('/example6a/{id}', middleware=[
        #     Guard(['authenticated', 'manager']),
        #     # Any other route based middleware here
        # ], tags=['Examples'])
        # async def example6a(request: Request, id: int, name: Optional[str]) -> models.Post:
        #     user = request.scope['user']
        #     dump(name, user)
        #     return await models.Post.query().find(id)

        # ----------------------------------------------------------------------
        # Example: Other types of responses
        # ----------------------------------------------------------------------
        # @route.get('/example6b')
        # async def example6b(request: Request):
        #     return response.Text('Text Here')
        #     return response.HTML('<b>HTML</b> here')
        #     return response.JSON({'json':'here'})
        #     return response.UJSON({'json':'here'}) # requires ujson dependency
        #     # and more ... see uvicore/http/response.py

        # ----------------------------------------------------------------------
        # Example: Changing the route name
        # Each route is given a name automatically.  A name is what you can use
        # to reference the route in your code and view templates.  Try to use the
        # route name instead of the path as paths WILL change as other users use
        # your library because they can tweak the BASE PATH.  Views should be using
        # {{ url('xx_appname.ex7')}}, never /example7
        # If you don't specify a name, uvicore makes a name automatically
        # from the path, even nested paths from groups.  Name always starts
        # with your apps name, ie: xx_appname.
        # ----------------------------------------------------------------------
        # @route.get('/example7', name='ex7')
        # async def example2a(request: Request):
        #     # Route name is xx_appname.ex7 instead of default xx_appname.example7
        #     return response.Text('example7')


        # ----------------------------------------------------------------------
        # Example: Override the naming autoprefix
        # When you define a custom route name, a prefix of xx_appname. is
        # automatically added keeping your route scoped to this package.
        # In order to set a full name you must set autoprefix=False.
        # This is handy when you want to override a route from another package.
        # ----------------------------------------------------------------------
        # @route.get('/example8', name='someother.app.ex8', autoprefix=False)
        # async def example8(request: Request):
        #     # Route name is someother.app.ex8
        #     return response.Text('example8')


        # ----------------------------------------------------------------------
        # Example: POST a model with validation
        # ----------------------------------------------------------------------
        # @route.post('/example9')
        # async def example9(post: models.Post):
        #     models.Post.insert(post)


        # ----------------------------------------------------------------------
        # Example raise proper HTTP Exception
        # ----------------------------------------------------------------------
        # @route.get('/example9a')
        # async def example9a():
        #     raise HTTPException(404, 'bad stuff')


        # ----------------------------------------------------------------------
        # Example: Grouping routes for common paths and scopes
        # Routes will be /group1/example10 and /group1/subgroup1/example11
        # with scopped permissions on both routes.
        # IF you also set name='g1', all route names will be
        # xx_appname.g1.example19 instead of autonamed xx_appname.group1.example10
        # ----------------------------------------------------------------------
        # @route.group('/group1', scopes=['authenticated'], tags=['Group'])
        # def group1():
        #     # Route will be under both Group and Example TAG
        #     @route.get('/example10', tags=['Example'])
        #     async def example10(request: Request):
        #         return response.Text("example10")

        #     @route.group('/subgroup1')
        #     def subgroup1():
        #         @route.get('/example11')
        #         async def example11(request: Request):
        #             return response.Text("example11")


        # ----------------------------------------------------------------------
        # Example: Routes as method callbacks (no decorators)
        # ----------------------------------------------------------------------
        # def example12(request: Request):
        #     return response.Text('example12')
        # route.get('/example12', example12)


        # ----------------------------------------------------------------------
        # Example: Groups and routes as method callbacks (no decorators)
        # ----------------------------------------------------------------------
        # def example13(request: Request, id: int) -> models.Post:
        #     return await models.Post.query().find(id)
        # def example14(request: Request, email: str) -> List[models.Post]:
        #     return await models.Post.query().where('email', email).get()
        # route.group('/group2', scopes=['authenticated', 'post_manager'], routes=[
        #     route.get('/example13', example13),
        #     route.get('/example14', example14),
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
