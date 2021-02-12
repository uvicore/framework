import uvicore
from uvicore import typing

# ModelRoute is the only class that cannot be EXTENDED becuase I am inspecting
# the class dynamically.  If you want to extend or change the ModelRoute you
# must re-impliment the entire class.

@uvicore.service()
class _ModelRoute:

    def routes(self, Model, route, path, tags):

        @route.get('/' + path, response_model=typing.List[Model], tags=tags)
        async def list(include: typing.Optional[str] = ''):
            return await Model.query().include(*include.split(',')).get()

        # @route.get('/' + path + '/{id}', response_model=Model, tags=tags)
        # async def get(id: typing.Any, include: typing.Optional[str] = ''):
        #     return await Model.query().include(*include.split(',')).find(id)

        # @route.post('/' + path, response_model=Model, tags=tags)
        # async def post(entity: Model):
        #     return entity
