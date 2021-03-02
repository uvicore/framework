import uvicore
import inspect
from uvicore import typing
from uvicore.http.routing.api_router import ApiRouter
from uvicore.http.routing.router import Routes as Controller
from uvicore.http.request import Request
from uvicore.support import str as string
from uvicore.support.dumper import dump, dd
from uvicore.support import module
from uvicore.orm.fields import Relation
from uvicore.http.exceptions import HTTPException


@uvicore.service()
class ModelRoute:
    """Dynamic Model CRUD Routes"""

    def routes(self, Model, route, path, tags):
        """Build dynamic model CRUD routes"""

        @route.get('/' + path, response_model=typing.List[Model], tags=tags)
        async def list(include: typing.Optional[str] = '', user: User = Guard(Model.tablename + '.read')):
            # The auth guard will not allow this method, but we do have to check any INCLUDES against that models permissions
            includes = include.split(',')
            return await Model.query().include(*includes).get()

        #@route.get('/' + path + '/{id}', response_model=Model, tags=tags)
        @route.get('/' + path + '/{id}', tags=tags)
        async def get(id: typing.Any, request: Request, include: typing.Optional[str] = '', user: User = Guard(Model.tablename + '.read')):
            # The auth guard will not allow this method, but we do have to check any INCLUDES against that models permissions
            includes = include.split(',') if include else []

            # Fix me, i already inject the User. if permissions were there, I don't need request at all!
            self.guard_include_permissions(includes, request)
            return await Model.query().include(*includes).find(id)

    def guard_include_permissions(self, includes: typing.List, request: Request):
        if not includes: return
        for include in includes:
            field = Model.modelfields.get(include)
            if not field: continue
            if not field.relation: continue
            relation: Relation = field.relation.fill(field)
            tablename = relation.entity.tablename
            permission = tablename + '.read'

            #FIXME, lets assume user_permissions are in the user model
            user_permissions = request.scope.get('user_permissions')
            if permission not in user_permissions:
                raise HTTPException(
                    status_code=401,
                    detail="Access denied to {}".format(tablename)
                )




        # @route.post('/' + path, response_model=Model, tags=tags)
        # async def post(entity: Model):
        #     return entity


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



@uvicore.controller()
class ModelRouter(Controller):

    def register(self, route: ApiRouter):

        # Get all models in tablename sorted order from Ioc bindings
        models = self.models()

        # Get source code for ModelRouter
        modelroute = inspect.getsource(ModelRoute)
        modelroute += "ModelRoute().routes(Model, route, path, tags)"

        from uvicore.auth.middleware import Guard
        from uvicore.auth.models import User

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
            permissions = Model.tablename

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
                'route': route,
                'path': path,
                'tags': tags,
                'uvicore': uvicore,
                'typing': typing,
                'User': User,
                'Guard': Guard,
                'Request': Request,
                'HTTPException': HTTPException,
            })

        # Return router
        return route

    def models(self) -> typing.OrderedDict:
        """Get all models in tablename sorted order from Ioc bindings"""
        models = typing.OrderedDict()
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
