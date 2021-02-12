import uvicore
from uvicore.support.dumper import dump, dd
from uvicore.http import Request, response, WebRouter, Controller

# This Controller does Nothing now, no package init
class Home2(Controller):

    # middleware: List = ['auth', 'limitter']
    # user: UserModel = Auth()

    def register(self, route: WebRouter):

        @route.get('/h2')
        def get(request: Request):
            return response.Text('H2 here')


        # Return router
        return route










#from uvicore.http.controllers.web import controller


# from uvicore.http.routing.web_router import WebRouterX
# from uvicore.support.dumper import dd, dump

# #import uvicore
# #package = uvicore.app.package('app1')
# #route = routes = router = WebRouter(uvicore.app, package, 'xx')


# # route: Routes = None
# app = uvicore.app
# package = uvicore.app.package('app1')
# route = WebRouter(app, package, '/mywebprefix', 'app1')


# @controller(route)
# class Home2:

#     auth: int = 0

#     @route.get('/h2')
#     def get(self):
#         pass

#     def get_router(self):
#         return route

