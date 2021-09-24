import uvicore
from uvicore.support.dumper import dump, dd
from uvicore.http import Request, response
from uvicore.http.routing import Controller, ApiRouter, AutoApi, Guard
from uvicore.typing import Optional, List

from app1 import models
from functools import partial
from uvicore.http import params

#from uvicore.auth import User
from uvicore.contracts import UserInfo


from pydantic import BaseModel
class HTTPMessage(BaseModel):
  #status_code: int
  message: str
  #detail: Optional[str]
  #extra: Optional[Dict]



@uvicore.controller()
class Post(Controller):

    #user: User = Auth(['post.controller'], guard='api')
    #user: User = Auth()
    #user: User = Guard()
    #auth = Guard()

    #scopes = ['authenticated']


    # There are 3 ways to add middleware

    # Method 1 (preferred) - this does a Guard['authenticated'] for you
    #scopes = ['authenticated']

    # Method 2 - this append shit guard to middleware[]
    #auth = Guard(['authenticated'])

    # Method 3 - manual middleware definition
    # middleware = [
    #     Guard(['authenticated'])
    # ]


    def register(self, route: ApiRouter):

        #@route.get('/post4', middleware=[Auth('model-perms')])
        #@route.get('/post4', auth=Guard('model-perms'))
        #@route.get('/post4', scopes=['posts.read'])
        @route.get('/post4',
            # responses={
            #     404: {
            #         'model': HTTPMessage,
            #         #'description': 'xyz here',
            #         #'content': {"application/json": HTTPMessage},
            #     },
            # },
        )
        #async def post4(id: str, user: User = Guard()) -> models.Post:
        async def post4(request: Request, user: UserInfo = Guard(['posts.read'])) -> models.Post:
            """This docstring shows up in OpenAPI Docs"""
            #dump('=============================================================')
            #dump('REQUEST __dict__ FROM /post4 CONTROLLER:')
            #dump('=============================================================')
            #dump(request.__dict__)
            dump('POST4 User:', user)
            return await models.Post.query().find(4)




        async def autoapi_list(
            request: Request,
            include: Optional[List[str]] = params.Query([]),
            where: Optional[str] = ''
        ):
            pass

        # @route.get('/post6')
        # @merge_args(default_get)
        # async def pp(more: str, **kwargs):
        #     dump(kwargs)
        #     include = kwargs.pop('include')
        #     dump(include)
        #     pass

        #from uvicore.http.routing.auto_api import autoapi_list2

        #@route.get('/post5', inherits=autoapi_list)
        @route.get('/post5/', inherits=AutoApi.listsig)
        #@route.get('/post5', response_model=models.Post, inherits=autoapi_list2)
        #@route.get('/post5', inherits=autoapi_list2)
        #async def post5(more: str, **kwargs) -> models.Post:
        async def post5(more: str, **kwargs):
            api = AutoApi[models.Post](models.Post, **kwargs).guard_relations()
            result = await api.orm_query().find(5)
            return result

        @route.post('/post5')
        async def post5_create():
            pass

        @route.put('/post5')
        async def post5_put():
            pass

        @route.patch('/post5')
        async def post5_patch():
            pass

        @route.delete('/post5')
        async def post5_delete():
            pass



        @route.add('/post6', methods=['PATCH', 'POST'])
        async def post6():
            pass

        @route.add('/post6', methods=['PUT', 'DELETE'], name='post6-PD')
        async def post6():
            pass

                # path='/post5',
                # name='app1.api.post5',
                # endpoint=app1.http.api.post.Post.register.<locals>.post5,  # function
                # methods=['GET'],
                # response_model=None,
                # tags=None,
                # middleware=[],
                # summary='summary-asdfasdf',
                # description='desc-asdfasdf',
                # original_path='/post5',
                # original_name='post5'




        # Return router
        return route








# from typing import List

# from app1.models.post import Post
# from app1.models.user import User
# from uvicore.http import ApiRouter
# from uvicore.support.dumper import dump, dd




# routes = route = ApiRouter()
# #router = route


# from fastapi.params import Depends, Security
# from uvicore.typing import Optional, Any, Callable, Sequence
# from uvicore.http import Request
# from fastapi.exceptions import HTTPException
# from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN
# from fastapi.security import SecurityScopes

# # Actual Auth route middleware
# class AuthMiddleware:
#     async def __call__(self, scopes: SecurityScopes, request: Request):
#         # Load the default auth guard defined for WebRoutes or APIRoutes
#         # Run that guard and get authorized=true/false with some user info perhaps
#         authorized = True  # from session or token...

#         dump(scopes, scopes.__dict__)

#         if authorized:
#             # Authorized, return user object
#             return {'auth': 'here'}
#         else:
#             raise HTTPException(
#                 status_code=HTTP_401_UNAUTHORIZED,
#                 detail="Not authenticated",
#                 headers={"WWW-Authenticate": "Bearer"},  # Change depending on session, basic etc...
#             )

# # Define from some HTTP kernel
# route_middleware = {
#     'auth': AuthMiddleware()
# }



# class Middleware(Security):
#     def __init__(
#         self,
#         dependency: Optional[Callable[..., Any]] = None,
#         scopes: Optional[Sequence[str]] = None,
#     ):
#         #self.dependency = route_middleware.get(middleware)
#         #self.use_cache = True
#         super().__init__(dependency=route_middleware.get(dependency), scopes=scopes, use_cache=True)


# # #@route.get('/posts', response_model=List[Post])
# # @route.get('/posts', middleware=['throttle', ])
# # async def posts(
# #     include: str = '',
# #     user: User = Middleware('auth', ['scope1', 'scope2'])
# # ):

# #     #return await Post.query().include(*include.split(',')).get()
# #     #dump(user)
# #     #return {'status': 'done'}
# #     return user







# @route.get('/posts/{id}', response_model=Post)
# async def post(id: int, include: str = ''):
#     return await Post.query().include(*include.split(',')).find(id)




# Auth, what I want

# a nice auth interface, which extends Depends and handles ANY form of auth
# basically if not logged in, fires the defined auth type (basic promps user/pass, oauth2 401...)
# if logged in, pulls user and scope from response or wherever
# Because its a Depends() it will 404 or 401 BEFORE the route hits, its like middleware per route
# This means auth cannot be middleware, but is PER route.  So an 'auth' config section, not under middleware
# If you don not deinfe auth=Auth() in params, its a PUBLIC route
# Laravel has a concept of ROUTE MIDDLEWARE, and route group middleware! This is basically Depends()
# In laravels http/Keronel you define a 'RouteMiddleware' array where you can give it a small key.
# Route middleware COULD be per package, but global middleware should not
# He can even split mittleware out into "groups" like 'web'[] and 'api'[], I should do this

# from somewhere import Auth
# @route.get('/posts', response_model=Post)
# async def post(auth: Auth = Guard()):  # If nothing defined, means at least must be AUTHENTICATED
# async def post(auth: Auth = Guard(['user.read', 'someother.scope'])):  # optionally limit this endpoint to a role
#     name = auth.user.name
#     roles = auth.user.roles
#     groups = auth.user.groups
#     etc...
#     #return await Post.query().include(*include.split(',')).find(id)




# from uvicore.http.middleware import Auth

# @route.get('/posts', response_model=Post)
# async def posts(
#     id: int,
#     name: str,
#     stuff: str,
#     user: User = Middleware('auth'), # uses default guard from config
#     user1: User = Middleware('auth:api'),  # uses API guard from config
# ):
#     pass

# Policy Methods
# viewAny
# view
# create
# update
# delete

# Middleware is called 'can' or 'cannot'

# user: User = Middleware('can', ['create', 'delete'], Post)

# Passing in the Post model lets us find the proper Policy
# By default we should have a policy for each model
# that uas viewAny, view, create, update, delete that simply
# looks to the users roles->permissions and find the right string.
# We can optionally overwrite any model policy to add things like
# def create():
#     if user.id == post.id...



# # laravel
# Route::get('/flights', function () {
#     // Only authenticated users may access this route...
# })->middleware('auth:admin');
