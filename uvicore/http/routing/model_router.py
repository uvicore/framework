import uvicore
from uvicore.typing import List, Any
from uvicore.http.routing.api_router import ApiRouter


class ModelRoute:
    def __init__(self, model, router, path: str):
        self.model = model
        self.router = router
        self.path = path

    def routes(self):
        # List
        self.router.add_route(
            path='/' + self.path,
            endpoint=self.list,
            response_model=List[self.model],
            name='Get all {}'.format(self.path),
        )

        # Get
        self.router.add_route(
            path='/' + self.path + '/{id}',
            endpoint=self.get,
            response_model=self.model,
            name='Get {} by ID'.format(self.path),
        )

    async def list(self):
        return await self.model.query().get()

    async def get(self, id: Any):
        return await self.model.query().find(id)


@uvicore.service()
class ModelRouter:  # Need Interface

    def routes(self):

        # New Api Router
        router = ApiRouter()

        # Get all models
        models = uvicore.ioc.binding(type='model')
        for key, binding in models.items():
            # Ignore BASE override models
            if binding.path != key: continue

            # Get actual model from Ioc binding object
            model = binding.object

            # Get URL path
            path = model.tablename

            # Add model routes
            ModelRoute(model, router, path).routes()

        # Return router
        #for r in router.routes: dump(r.__dict__)
        #exit()
        #dd(route.routes)
        return router
