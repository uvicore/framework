from uvicore.http import Request, response, WebRouter
from uvicore.support.dumper import dd, dump

route = routes = router = WebRouter()


from uvicore.http.controllers import WebController
from uvicore.http.request import Form





from fastapi.params import Depends, Security
from uvicore.typing import Optional, Any, Callable, Sequence
from uvicore.http import Request
from fastapi.exceptions import HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_429_TOO_MANY_REQUESTS
from fastapi.security import SecurityScopes
from app1.models.user import User
from starlette.middleware.base import BaseHTTPMiddleware

# Actual Auth route middleware
class AuthMiddleware:
    async def __call__(self, scopes: SecurityScopes, request: Request):
        # Load the default auth guard defined for WebRoutes or APIRoutes
        # Run that guard and get authorized=true/false with some user info perhaps
        authorized = True  # from session or token...

        dump(scopes, scopes.__dict__)

        if authorized:
            # Authorized, return user object
            return {'auth': 'here'}
        else:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},  # Change depending on session, basic etc...
            )


# Example of fake middleware that returns nothing
class RateLimitMiddleware:
    async def __call__(self, request: Request):
        # Load the default auth guard defined for WebRoutes or APIRoutes
        # Run that guard and get authorized=true/false with some user info perhaps
        rate_exceeded = False

        if rate_exceeded:
            raise HTTPException(
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                detail="Fake Too many requests",
            )


# Example of fake middleware that returns nothing
class EmptyMiddlewareXXX:
    async def __call__(self, request: Request):
        # Load the default auth guard defined for WebRoutes or APIRoutes
        # Run that guard and get authorized=true/false with some user info perhaps
        deny = True

        if deny:
            raise HTTPException(
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                detail="Fake Empty",
            )


# My Own base middleware
class Base(BaseHTTPMiddleware):


    async def __call__(self, request: Request):
        # Route based DEPENDS middleware



    async def dispatch(self, request, call_next):
        # Global middleware

        # Do stuff to the Request here

        # Call next middleware
        response = await call_next(request)

        # Do stuff to the Response here
        #response.headers['Custom'] = 'Example'
        self.handle(request)

        # Return response
        return response




# Example of fake middleware that returns nothing
class EmptyMiddleware(BaseHTTPMiddleware):

    def __init__(self, app = None):
        if app is None:
            # Using as Route based middleware
            pass
        else:
            # Using as global middleware
            super().__init__(app)

    async def handle(self):




    async def __call__(self, request: Request):
        # Load the default auth guard defined for WebRoutes or APIRoutes
        # Run that guard and get authorized=true/false with some user info perhaps
        deny = True

        if deny:
            raise HTTPException(
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                detail="Fake Empty",
            )

    async def dispatch(self, request, call_next):
        response = await call_next(request)

        deny = True

        if deny:
            raise HTTPException(
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                detail="Fake Empty",
            )

        return response


# Define from some HTTP kernel
route_middleware = {
    'auth': AuthMiddleware(),
    'limiter': RateLimitMiddleware(),
    'empty': EmptyMiddleware(),
}


# This is the DEPENDS class itself
class Auth(Security):
    def __init__(
        self,
        #dependency: Optional[Callable[..., Any]] = None,
        scopes: Optional[Sequence[str]] = None,
    ):
        #self.dependency = route_middleware.get(middleware)
        #self.use_cache = True
        super().__init__(dependency=route_middleware.get('auth'), scopes=scopes, use_cache=True)


# This is the DEPENDS class itself
class Middleware(Depends):
    def __init__(
        self,
        name: Optional[Callable[..., Any]] = None,
    ):
        super().__init__(dependency=route_middleware.get(name), use_cache=True)




@WebController(router)
class Controller:

    user: User = Auth(['scope1', 'scope2'])
    limiter: bool = Middleware('limiter')
    empty: bool = Middleware('empty')

    @route.get('/', name='home')
    async def get(self, request: Request):

        return response.View('app1/home.j2', {
            'request': request,
            'user': self.user,
        })
        # return response.HTML("""
        # <b>Hi</b> there.

        # """)

    @route.post('/form')
    async def post(self, request: Request, name: str = Form(...)):
        # Where body is form data like name=matthew
        # http -v --form POST http://localhost:5000/app1/2 name=there
        #return response.Text(name)
        return response.View('app1/home.j2', {
            'request': request,
            'user': self.user,
            'name': name,
        })

        #raise HTTPException(HTTP_500_INTERNAL_SERVER_ERROR, 'Bad stuff he re')







# @route.get('/', name='home')
# async def home(request: Request, name: str = None):

#     return response.View('app1/home.j2', {
#         'request': request,
#         'name': name2,
#     })
#     # return response.HTML("""
#     # <b>Hi</b> there.

#     # """)

# # from uvicore.http import Body, Form
# # @route.post('/')
# # async def home_post(name: str = Body(..., embed=True)):
# #     # Where body is JSON data like {'name': 'matthew'}
# #     # http -v POST http://localhost:5000/app1/ name=there
# #     # echo '{"name": "matthew"}' | http -v POST http://localhost:5000/app1/
# #     return response.Text(name)

# from uvicore.http.exceptions import HTTPException
# from uvicore.http.status import HTTP_500_INTERNAL_SERVER_ERROR

# @route.post('/form')
# async def home_post(request: Request):
#     # Where body is form data like name=matthew
#     # http -v --form POST http://localhost:5000/app1/2 name=there
#     #return response.Text('asdf')
#     raise HTTPException(HTTP_500_INTERNAL_SERVER_ERROR, 'Bad stuff he re')

