import uvicore
from uvicore.typing import List, Any
from uvicore.http.routing.api_router import ApiRouter
from uvicore.typing import TypeVar, Generic, OrderedDict, Dict
from uvicore.support import str as string
from uvicore.support.dumper import dump, dd

E = TypeVar("E")

#from app1.models import Hashtag

class ModelRoute(Generic[E]):
    def __init__(self, Model: E, router: ApiRouter, path: str):
        self.Model: E = Model
        self.router: ApiRouter = router
        self.path: str = path

    def routes(self):
        tags = [string.ucbreakup(self.path)]

        # GET List
        self.router.add_api_route(
            path='/' + self.path,
            methods=['GET'],
            tags=tags,
            endpoint=self.list,
            response_model=List[self.Model],
            name='Get all {}'.format(self.path),
            #name=self.path,
            #   name='',
        )

        # GET
        self.router.add_api_route(
            path='/' + self.path + '/{id}',
            methods=['GET'],
            tags=tags,
            endpoint=self.get,
            response_model=self.Model,
            name='Get {} by ID'.format(self.path),
            #name=self.path,
            #name='',
        )

        # POST
        self.router.add_api_route(
            path='/' + self.path,
            methods=['POST'],
            tags=tags,
            endpoint=self.post,
            response_model=self.Model,
            name='Create {}'.format(self.path),
            #name=self.path,
            #name='',
        )

    async def list(self, include: str = ''):
        return await self.Model.query().include(*include.split(',')).get()

    async def get(self, id: Any, include: str = ''):
        return await self.Model.query().include(*include.split(',')).find(id)

    async def post(self, entity):
        dump(entity)
        return entity
        #return await self.Model.query().include(*include.split(',')).find(id)



@uvicore.service()
class ModelRouter:  # Need Interface

    def routes(self):

        # New Api Router
        router = ApiRouter()

        # Get all models in tablename sorted order
        models = self._get_models()

        # Loop each sorted model and dynamically add a ModelRouter
        for key, binding in models.items():
            # Get actual model from Ioc binding object
            Model = binding.object

            # Get URL path
            path = Model.tablename

            # Add model routes
            ModelRoute[Model](Model, router, path).routes()

        # Return router
        #for r in router.routes: dump(r.__dict__)
        #exit()
        #dd(route.routes)
        return router

    def _get_models(self) -> OrderedDict:
        """Get all models in tablename sorted order"""
        models = OrderedDict()
        unsorted_models = {}
        model_bindings = uvicore.ioc.binding(type='model', include_overrides=False)
        for key, binding in model_bindings.items():
            tablename = binding.object.tablename
            if tablename not in models:
                unsorted_models[tablename] = binding

        # Sort the OrderedDict
        #import operator
        #x = sorted(models.items(), key=lambda x: x[1])
        #x = sorted((value, key) for (key,value) in models.items())
        keys = sorted(unsorted_models.keys())
        for key in keys:
            models[key] = unsorted_models[key]
        return models
