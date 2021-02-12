import uvicore
import inspect
from uvicore import typing
from uvicore.http.routing.api_router import ApiRouter
from uvicore.typing import TypeVar, Generic, OrderedDict, Dict
from uvicore.support import str as string
from uvicore.support.dumper import dump, dd
from uvicore.http import Request
from uvicore.support import module


@uvicore.service()
class _ModelRoute:

    def routes(self, Model, route, path, tags):

        @route.get('/' + path, response_model=typing.List[Model], tags=tags)
        async def list(include: typing.Optional[str] = ''):
            return await Model.query().include(*include.split(',')).get()

        @route.get('/' + path + '/{id}', response_model=Model, tags=tags)
        async def get(id: typing.Any, include: typing.Optional[str] = ''):
            return await Model.query().include(*include.split(',')).find(id)

        @route.post('/' + path, response_model=Model, tags=tags)
        async def post(entity: Model):
            return entity


        # # GET List
        # router.add_api_route(
        #     path='/' + path,
        #     methods=['GET'],
        #     tags=tags,
        #     endpoint=self.list,
        #     response_model=List[Model],
        #     name='Get all {}'.format(path),
        #     #name=path,
        #     #   name='',
        # )

        # # GET
        # router.add_api_route(
        #     path='/' + path + '/{id}',
        #     methods=['GET'],
        #     tags=tags,
        #     endpoint=self.get,
        #     response_model=Model,
        #     name='Get {} by ID'.format(path),
        #     #name=path,
        #     #name='',
        # )

        # # POST
        # router.add_api_route(
        #     path='/' + path,
        #     methods=['POST'],
        #     tags=tags,
        #     endpoint=self.post,
        #     response_model=Model,
        #     name='Create {}'.format(path),
        #     #name=path,
        #     #name='',
        # )

    # async def list(self, include: str = ''):
    #     return await Model.query().include(*include.split(',')).get()

    # async def get(self, id: Any, include: str = ''):
    #     return await Model.query().include(*include.split(',')).find(id)

    # async def post(self, entity: Model):
    #     #dump(request.__dict__)
    #     return entity
    #     #return {'name': 'hi'}
    #     #return await Model.query().include(*include.split(',')).find(id)



@uvicore.service()
class ModelRouter:  # Need Interface

    def routes(self):

        # New Api Router
        router = ApiRouter()

        # Get all models in tablename sorted order
        models = self._get_models()

        # Get source code for ModelRouter
        modelroute = inspect.getsource(_ModelRoute)
        modelroute += "_ModelRoute().routes(Model, router, path, tags)"

        # Loop each sorted model and dynamically add a ModelRouter
        for key, binding in models.items():
            # Temp, only hashtag
            #if binding.object.tablename != 'hashtags': continue

            # Get model information from Ioc binding
            Model = binding.object
            modelname = binding.path.split('.')[-1]
            tablename = Model.tablename
            path = tablename
            tags = [string.ucbreakup(path)]

            # Dynamically instantiate ModelRouter from source code and exec
            # passing in the proper globals.  Why?  Why not just instantiate
            # the class and be done?  Becuase pydantic doesn't understand
            # type hinting that way.  For example post(entity: Model) does NOT
            # work as the type hinter errors on the Model.  I tried every other way
            # and type hinting just does not work as expected.  Even with Generics[E]
            # Not sure why exactly. This dynamic execution however works for now.
            # One caveat to this is you cannot override and EXTEND the ModelRoute
            # class.  You can override, but you must re-impliment the entire class
            # and not just extend it.
            exec(modelroute, {
                'Model': Model,
                'router': router,
                'path': path,
                'tags': tags,
                'uvicore': uvicore,
                'typing': typing,
            })

        # Return router
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
























#             list_method = """
# @router.get('/' + path, response_model=List[Model], tags=tags)
# async def list(include: str = ''):
#     return await Model.query().include(*include.split(',')).get()
# """

#             get_method = """
# @router.get('/' + path + '/{id}', response_model=Model, tags=tags)
# async def get(id: Any, include: str = ''):
#     return await Model.query().include(*include.split(',')).find(id)
# """

#             post_method = """
# @router.post('/' + path, response_model=Model, tags=tags)
# async def post(entity: Model):
#     return entity
# """

#             # Add dynamic methods
#             exec(list_method, exec_globals)
#             exec(get_method, exec_globals)
#             exec(post_method, exec_globals)
