import uvicore
from uvicore.auth.models import User
from uvicore.auth.middleware.auth import Guard
from uvicore.support.dumper import dump, dd
from uvicore.http import Request, response
from uvicore.http.routing import Routes, WebRouter


# Final word in flat vs def vs Class with def.
# I want a class, so I can add auth or middleware instance variables just like
# I would in a controller.  Now routes and controllers are identical, basically just a massive
# nested routing system.

@uvicore.routes()
class Web(Routes):

    # If I wanted to apply global auth to every route, I could do it here
    user: User = Guard(['posts.read'], guard='web')

    def register(self, route: WebRouter):

        # Define controller base path
        route.controllers = 'app1.http.controllers'

        # Public Routes
        route.controller('home')
        route.controller('about')
        route.controller('login')


        # Private Routes
        #@route.group(auth=Guard(['scope0'], guard='api'))
        @route.group()
        def private():
            route.controller('admin')




        # async def get_method(request: Request):
        #     return response.Text('Get Method Here!')

        # # Raw add with methods
        # route.add('/get_method1', get_method, ['GET'])

        # # Get method helper
        # route.get('/get_method2', get_method, name='ad')

        # # Original wiki fake
        # #route.get('/search', get_method, autoprefix=False, name='wiki.search')

        # # No autoname or prefix, to override another packages routes
        # # I could get the
        # #wiki_prefix = '/wiki'  # I could get this from self.app.package('mreschke.wiki').web.prefix
        # #route.add(wiki_prefix + '/search', get_method, ['GET'], name='wiki.search', autoprefix=False) #, name=newname

        # # Or to override I can use this special method
        # #route.override('mreschke.wiki', 'wiki.search', get_method)

        # # Attempt override another apps route


        # #@route.get('/get_decorator1', required=['authenticated', 'admin'])
        # @route.get('/get_decorator1')
        # async def get(request: Request):
        #     return response.Text('Get Decorator Here!')

        # # # OVERRIDE a BUNCH of other packages routes
        # # route.group(prefix='/wiki', autoprefix=False, routes=[
        # #     route.get('/search', get_method),
        # # ])
        # # route.get('/wiki/search2', get_method, name='search', autoprefix=False)


        # # route.group(prefix='/abc/xyz', name='az', routes=[
        # #     route.get('/about/stuff', get_method, name='abouz'),
        # # ])


        # from app1.http.controllers.home2 import Home2
        # # # route.controller(Home2, prefix='home2')


        # Administration
        # route.group('/admin', autoprefix=True, routes=[
        #     route.get('/profile', get_method),
        #     #route.get('/settings', get_method),
        #     #route.get('/payments', get_method),

        #     #route.controller(Home2)
        #     #route.controller(Home2, prefix='home2'),

        #     route.group(prefix='/settings', routes=[
        #         route.get('/gears', get_method),

        #         route.controller(Home2, prefix='home3')
        #     ])


        # ])




        # @route.group(prefix='/y', name='y.')
        # def about_group():
        #     @route.get('/5')
        #     def get():
        #         pass



        # route.routes = [
        #     route.get('/4', get_method),
        # ]


        # Return router
        return route


# class Web(Routes[WebRouter]):

#     endpoints: str = 'app1.http.controllers'

#     def register(self):


#         #self.include('rapidoc')

#         self.include('home')
