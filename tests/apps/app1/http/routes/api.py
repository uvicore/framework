from uvicore.support.dumper import dump, dd
from uvicore.http import Request, response, Routes, ApiRouter


class Api(Routes):

    def register(self, route: ApiRouter):

        async def get_method(request: Request):
            return response.Text('Get API Method Here!')

        # Raw add with methods
        route.add('/get_method1', get_method, ['GET'])

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


        return route
