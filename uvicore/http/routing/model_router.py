import uvicore
import inspect
from uvicore import typing
from uvicore.http.routing.api_router import ApiRouter
from uvicore.http.routing.router import Routes as Controller
from uvicore.http.request import Request
from uvicore.support import str as string
from uvicore.support.dumper import dump, dd
from uvicore.support import module
from uvicore.http.exceptions import HTTPException, PermissionDenied
#from uvicore.auth import User
from uvicore.contracts import User
from uvicore.http.routing import Guard


@uvicore.service()
class ModelRoute:
    """Dynamic Model CRUD Routes"""

    def routes(self, Model, route, path, tags, scopes):
        """Build dynamic model CRUD routes"""

        @route.get('/' + path, response_model=typing.List[Model], tags=tags, scopes=[Model.tablename + '.read'] if scopes is None else scopes)
        #async def list(include: typing.Optional[str] = '', user: User = Guard(Model.tablename + '.read')):
        async def list(request: Request, include: typing.Optional[str] = ''):
            user: User = request.user
            # The auth guard will not allow this method, but we do have to check any INCLUDES against that models permissions
            includes = include.split(',') if include else []

            self.guard_include_permissions(Model, includes, user)
            return await Model.query().include(*includes).cache().get()

        #@route.get('/' + path + '/{id}', response_model=Model, tags=tags)
        @route.get('/' + path + '/{id}', tags=tags, scopes=[Model.tablename + '.read'] if scopes is None else scopes)
        #async def get(id: typing.Any, include: typing.Optional[str] = '', user: User = Guard(Model.tablename + '.read')):
        async def get(request: Request, id: typing.Any, include: typing.Optional[str] = ''):
            user: User = request.user
            # The auth guard will not allow this method, but we do have to check any INCLUDES against that models permissions
            includes = include.split(',') if include else []

            self.guard_include_permissions(Model, includes, user)
            return await Model.query().include(*includes).cache().find(id)

    def guard_include_permissions(self, Model, includes: typing.List, user: User):
        # No includes, skip
        if not includes: return

        # User is superadmin, allow
        if user.superadmin: return

        # Loop each include and parts
        for include in includes:

            # Includes are split into dotnotation "parts".  We have to walk down each parts relations
            parts = [include]
            if '.' in include: parts = include.split('.')

            entity = Model
            for part in parts:

                # Get field for this "include part".  Remember entity here is not only Model, but a walkdown
                # based on each part (separated by dotnotation)
                field = entity.modelfields.get(part)  # Don't use modelfield() as it throws exception

                # Field not found, include string was a typo
                if not field: continue

                # Field has a column entry, which means its NOT a relation
                if field.column: continue

                # Field is not an actual relation
                if not field.relation: continue

                # Get actual relation object
                relation = field.relation.fill(field)

                # Get model permission string for this relation
                model_permissions = [relation.entity.tablename + '.read'] if scopes is None else scopes

                # User must have ALL scopes defined on the route (an AND statement)
                authorized = True
                missing_scopes = []
                for scope in model_permissions:
                    if scope not in user.permissions:
                        authorized = False
                        missing_scopes.append(scope)

                # # Check if user has permissino to child relatoin (or superadmin)
                # if model_permission not in user.permissions:
                #     # I convert model_permissins to a list for consistency with other permission denied errors
                #     # although there will always be just one model_permission in this function
                #     # raise HTTPException(
                #     #     status_code=401,
                #     #     detail="Permission denied to {}".format(str([model_permission]))
                #     # )
                #     print('be')
                #     raise PermissionDenied(model_permission)

                if not authorized:
                    raise PermissionDenied(missing_scopes)

                # Walk down each "include parts" entities
                entity = relation.entity



            # if not field: continue
            # if not field.relation: continue
            # relation: Relation = field.relation.fill(field)
            # tablename = relation.entity.tablename
            # permission = tablename + '.read'

            # # Check if user has permissino to child relatoin (or superadmin)
            # if user.superadmin == False and permission not in user.permissions:
            #     raise HTTPException(
            #         status_code=401,
            #         detail="Access denied to {}".format(tablename)
            #     )




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

    def __init__(self, package, scopes: typing.List = None):
        """Init override to add custom guards parameter"""
        super().__init__(package)
        self.scopes = scopes

    def register(self, route: ApiRouter):

        # Get all models in tablename sorted order from Ioc bindings
        models = self.models()

        # Get source code for ModelRouter
        modelroute = inspect.getsource(ModelRoute)
        modelroute += "ModelRoute().routes(Model, route, path, tags, scopes)"

        #from uvicore.auth.middleware import Guard
        #from uvicore.auth.models import User


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
                'PermissionDenied': PermissionDenied,
                'scopes': self.scopes,
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
