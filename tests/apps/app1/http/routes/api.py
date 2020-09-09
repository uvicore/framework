from uvicore.http.routing import ApiRouter, Routes
from uvicore.support.dumper import dump, dd
from uvicore import app, config


class Api(Routes[ApiRouter]):

    endpoints: str = 'app1.http.api'

    def register(self):
        # Available instance variables:
        # self.app, self.package, self.Router, self.prefix

        # If you defined a self.endpoints you can use string based module lookup
        self.include('post', tags=['Posts'])

        # Or just import the module and pass in the route directly
        #from mreschke.wiki.http.endpoints import user
        #self.include(user.route, tags=['Users'])


        # # Include controller routes
        # self.controller(home)
        # self.controller(about)
        # self.controller(starlette, prefix="/starlette")

        # #app.dd(self.package)

        # Define inline routes if needed
        # NO, does not work now
        # @router.get('/hello')
        # async def test():
        #     return {"hello":"world"}

        # If you really wanted to define inline routes, have to do it like this
        route = self.Router()
        @route.get('/hello')
        async def hello():
            return {"hello":"world"}
        self.include(route, tags=['extra'])



        # Example adding a second router to define different tags
        # Simply make a new Router() and another self.include()
        route = self.Router()
        @route.get('/hello2')
        async def hello2():
            return {"hello":"world2"}
        self.include(route, tags=['extra2'])


        # from fastapi.responses import HTMLResponse
        # @http.get(prefix + '/about', response_class=HTMLResponse, tags=["asdf"])
        # async def about():
        #     html = "<b>Hi</b> there"
        #     #return HTMLResponse(content=html, status_code=200)
        #     return html








# from fastapi import APIRouter
# from uvicore import app

# api = APIRouter()

# @api.get('/api/about')
# async def about():
#     return {"message": "About Here"}


# app.http.include_router(api)
