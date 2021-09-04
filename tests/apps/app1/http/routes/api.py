import uvicore
from uvicore.support.dumper import dump, dd
from uvicore.http import Request, response
from uvicore.http.routing import Routes, ApiRouter, ModelRouter

from app1.models.post import Post

#from uvicore.auth.middleware import Guard
from uvicore.http.routing import Guard

from uvicore.auth.models import User
from uvicore.contracts import UserInfo

from app1.http.api.post import Post as PostController
from datetime import datetime


@uvicore.routes()
class Api(Routes):

    #user: User = Guard(['asdf'], guard='api')
    #x: str = 'xx'
    #guard: str = 'web'
    #user: User = Guard(['admin'])
    #auth = Guard(['scope0'], guard='api')

    #scopes = ['authenticated']

    def register(self, route: ApiRouter):
        """Register API Route Endpoints"""

        # Define controller base path
        route.controllers = 'app1.http.api'

        # Include dynamic model CRUD API endpoints (the "auto API")!
        #@route.group(auth=Guard(['scope-AUTO'], guard='api'))
        #@route.group(scopes=['authenticated', 'api.access'])
        #@route.group(scopes=['authenticated'])
        @route.group()
        def autoapi():
            # I should add a flag to NOT auto add Guard() to each model endpoint
            # If I wanted a fully public model router
            route.include(ModelRouter, options=uvicore.config.app.api.auto_api)

        # Rapidoc experiment
        route.controller('rapidoc')


        async def get_method() -> Post:
            #return response.Text('Get API Method Here!')
            return await Post.query().find(1)

        # # Raw add with methods
        # #route.add('/get_method1', get_method, ['GET'], response_model=Post)  # Or infer response_model
        route.add('/get_method1', get_method, ['GET'])


        @route.group(scopes=['posts.read'])
        #@route.group(auth=Guard(['scope1', 'scope2'], guard='api'))
        #@route.group(scopes=['scope1', 'scope2'])
        def ping_group():

            #@route.get('/ping', auth=Guard(['scope32']))
            #@route.get('/ping', middleware=[Guard('scope323')])
            @route.get('/ping')
            #@route.get('/ping', scopes=['posts.create'])
            #def ping(request: Request, user: User = Guard(['scope4'])):
            def ping(request: Request, user: UserInfo = Guard(['posts.read'])):
            #def ping(request: Request, user: User):  # If I hacked FastAPI dep code
            #def ping(request: Request, user: User = User()):  # If I made a depends Class like my old Guard()
                #user: User = request.user
                dump('PING USER', user)


                #user = request.scope.get('user')
                #dump(user)
                #dump(user.name)
                #dump(user.permissions)
                #dump(user.can(['posts.read', 'comments.read']))

                #if user.can('posts.read'):
                #    dump('yes user can posts.read')

                return {
                    'message': 'pong {}'.format(datetime.now()),
                    #'user': user
                }


        @route.group()
        def test():
            route.include('post')
            # @route.get('/ping2')
            # def ping():
            #     return {'message': 'pong {}'.format(datetime.now())}


        @route.group()
        def public_api():

            @route.get('/public')
            def pub(request: Request):
                user = request.scope.get('user')
                return {
                    'message': 'public endpoint here',
                    'user': user
                }



        # #@route.get('/post2', tags=["Post"], middleware=[Guard(['admin'])])
        # @route.get('/post2', tags=["Post"])
        # #async def post2(request: Request) -> Post:  # Request injected!
        # #async def post2(user: User = BasicAuth(['admin'])):
        # #async def post2(user: User = self.auth(['admin'], guard='api')):
        # #async def post2(user: User = Guard()(['admin'])):
        # #async def post2(user: User = Guard(['admin'])):
        # #async def post2(user: User = self.user):
        # async def post2():
        #     #return await Post.query().find(1)
        #     return '/post2'

        # # # BUG FOUND, if /post2 exists above, it replaces it with this one below
        # # route.group('/group1', routes=[
        # #     route.get('/post2', post3)
        # # ])

        # @route.group('/group1')
        # # @route.group('/group1', middleware=[
        # #     Guard(['asdf'], guard='api')
        # # ])
        # def group1():

        #     @route.get('/post3')
        #     #async def post3(user: User = self.user):
        #     async def post3(request: Request):
        #     #async def post3(request: Request, user: User = Guard(['asdf'])):
        #         #return '/group1/post3'
        #         user: User = request.scope.get('user')
        #         return user



        #     route.controller(PostController)



        # Return router
        return route






# class Api(Routes[ApiRouter]):

#     endpoints: str = 'app1.http.api'

#     def routes(self):
#         route = self.new_router()


#         # Inline route decorators
#         from app1.models import Post
#         from uvicore.typing import List
#         @route.get('/posts2', response_model=List[Post], tags=['Posts'])
#         async def post():
#             return await Post.query().get()



#         # Direct view routes - NO, not on API router
#         #route.view('/about', 'app1/about.j2')


#         # Controller route by class
#         #from app1.http.api import post
#         #route.resource(post.route, tags=['asdf'])

#         # Controller by string
#         route.resource('post.routes', tags=['asdf'])







        # Auto API Experiment
        #route.resource(ModelRouter().routes())


        # Test
        #self.include('test', tags=['Test'])

        #self.include('post', tags=['Posts'])
        #self.include('user', tags=['Users'])












        #uvicore.app.http.include_router(route)



        #route.get('/asdf', controller='posts:index', middleware='')

        # Import entire controller router
        #route.resource('app1.http.api.about', prefix='/about', middleware=['asdf'])
        #route.resource('about')

        #route.redirect('/here', '/there', 301)

        # only view, no controller, so no view data
        #route.view('/viewonly', 'wiki/someview.j2')

        #route.domain('something.else.com')


