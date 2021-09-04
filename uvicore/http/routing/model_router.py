import uvicore
import inspect
import fnmatch
from uvicore.typing import Optional, List, Tuple, Dict, Any, OrderedDict, Union
from uvicore.http.routing.api_router import ApiRouter
from uvicore.http.routing.router import Routes as Controller
from uvicore.http.request import Request
from uvicore.support import str as string
from uvicore.support.dumper import dump, dd
from uvicore.support import module
from uvicore.http.exceptions import HTTPException
from uvicore.contracts import UserInfo
from uvicore.http.routing import Guard
from uvicore.orm import Model as OrmModel
from uvicore.http.routing.auto_api import AutoApi
from uvicore.support.collection import setvalue


@uvicore.service()
class ModelRoutes:
    """Dynamic Model CRUD Routes"""

    @property
    def log(self):
        return uvicore.log.name('uvicore.model_router')

    def register(self, Model: OrmModel, route: ApiRouter, path: str, tags: List, scopes: List):
        """Build dynamic model CRUD routes"""

        #@route.get('/' + path, inherits=AutoApi.listsig, response_model=List[Model], tags=tags, scopes=[Model.tablename + '.read'] if scopes is None else scopes)
        @route.get('/' + path, inherits=AutoApi.listsig, response_model=List[Model], tags=tags, scopes=scopes['read'])
        async def list(**kwargs):
            api = AutoApi(Model, scopes, **kwargs).guard_relations()
            query = api.orm_query()

            # Run ORM query for results
            try:
                results = await query.get()
                return results
            except Exception as ex:
                dump(ex)
                raise HTTPException(500, str("Error in query builder, most likely an unknown column or query parameter."))

        @route.get('/' + path + '/{id}', inherits=AutoApi.getsig, response_model=Model, tags=tags, scopes=scopes['read'])
        async def get(id: Union[str,int], **kwargs):
            api = AutoApi(Model, scopes, **kwargs).guard_relations()
            query = api.orm_query()

            # Run ORM query for results
            try:
                results = await query.find(id)
                return results
            except:
                raise HTTPException(500, str("Error in query builder, most likely an unknown column or query parameter."))


        #@route.post('/' + path, response_model=Model, tags=tags, scopes=scopes['create'])
        @route.post('/' + path, response_model=Model, tags=tags, scopes=scopes['create'])
        async def post(request: Request, item: Model):
            # NOTES
            # How do I check each child relations permissions, there is no includes
            # Would have to flip each item key and check if its a relation?
            # Then check if user has access to that relation?

            # Insert into storage and return primary key inserted
            try:
                pk = await Model.insert(item)

                # If primary key is read_only, assume its an auto-incrementing pk
                # If not read_only, its a manual pk like 'key'.
                # Only set new pk result if pk is read_only.  Why? Because when pk is 'key'
                # a string, encode/databases does not return the new pk, just returns 1 every time.
                if Model.modelfield(Model.pk).read_only == True:
                    setvalue(item, Model.pk, pk)

                # Return inserted item
                #dump(item)
                return item

            except Exception as e:
                raise HTTPException(500, str(e))


        # #@route.post('/' + path, response_model=Model, tags=tags, scopes=scopes['create'])
        # @route.post('/' + path + '/with_relations', response_model=Model, tags=tags, scopes=scopes['create'])
        # async def post(request: Request, item: Dict):
        #     # NOTES
        #     # How do I check each child relations permissions, there is no includes
        #     # Would have to flip each item key and check if its a relation?
        #     # Then check if user has access to that relation?

        #     # Insert into storage and return primary key inserted
        #     try:
        #         pk = await Model.insert_with_relations([item])
        #         #pk= await Model.insert(item)

        #         # If primary key is read_only, assume its an auto-incrementing pk
        #         # If not read_only, its a manual pk like 'key'.
        #         # Only set new pk result if pk is read_only.  Why? Because when pk is 'key'
        #         # a string, encode/databases does not return the new pk, just returns 1 every time.
        #         if Model.modelfield(Model.pk).read_only == True:
        #             setvalue(item, Model.pk, pk)

        #         # Return inserted item
        #         #dump(item)
        #         return item

        #     except Exception as e:
        #         raise HTTPException(500, str(e))




@uvicore.controller()
class ModelRouter(Controller):
    """Automatic CRUD Model Router"""

    # Notice.  This is actually must a regular uvicore route controller!
    # Just like any of your other controllers.  The only difference
    # is the register() is dynamically registering CRUD endpoints
    # for a dynamic list of all your models!

    def __init__(self, package, scopes: List = None, include: List = None, exclude: List = None):
        """Init override to add custom parameter"""

        # To add options from your routes/api.py use
        # route.include(ModelRouter, options={'scopes': []})
        super().__init__(package)
        self.scopes = scopes
        self.include = include
        self.exclude = exclude

    def register(self, route: ApiRouter):
        """Register API Route Endpoints"""

        # Get all models in tablename sorted order from Ioc bindings
        # This obeys self.include and self.exclude
        models = self._get_all_ioc_models()

        # Get source code for ModelRouter
        #modelroute = inspect.getsource(ModelRoute)
        #modelroute += "ModelRoute().routes(Model, route, path, tags, scopes)"

        # Loop each sorted model and dynamically add a ModelRouter
        for key, binding in models.items():

            # Get model information from Ioc binding
            Model = binding.object
            modelname = binding.path.split('.')[-1]
            tablename = Model.tablename
            path = tablename
            tags = [string.ucbreakup(path)]
            permissions = Model.tablename

            # Get CRUD scopes plus any custom scopes
            scopes = self._get_scopes(tablename)
            #dump("FULL SCOPES: ", scopes)

            # Instantiate our ModelRouter class with this one Uvicore model
            ModelRoutes().register(Model, route, path, tags, scopes)


            # OLD - This was when I was using FastAPIs route directly instead
            # of my new uvicore router abstraction.  Now with uvicore router
            # all of this dynamic inspect exec() is not needed!!!
            # ------------------------------------------------------------------
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
            # exec(modelroute, {
            #     'Model': Model,
            #     'route': route,
            #     'path': path,
            #     'tags': tags,
            #     'uvicore': uvicore,
            #     'typing': typing,
            #     'UserInfo': UserInfo,
            #     'Guard': Guard,
            #     'Request': Request,
            #     'HTTPException': HTTPException,
            #     'PermissionDenied': PermissionDenied,
            #     'scopes': self.scopes,
            #     'dump': dump,
            #     'json': json,
            #     'params': params,
            # })

        # Return router
        return route

    def _get_all_ioc_models(self) -> OrderedDict:
        """Get all models in tablename sorted order from Ioc bindings"""
        models = OrderedDict()
        unsorted_models = {}
        model_bindings = uvicore.ioc.binding(type='model', include_overrides=False)

        all_model_keys = set(model_bindings.keys())
        model_keys = []

        # If include, only include these models (wildcards accepted)
        if self.include:
            for include in self.include:
                model_keys.extend(fnmatch.filter(all_model_keys, include))

            # Ensure unique List in case of double include entries matching double
            model_keys = list(set(model_keys))
        else:
            # No includes, use all models
            model_keys = all_model_keys

        # If exclude, remove them from the list (wildcards accepted)
        if self.exclude:
            for exclude in self.exclude:
                model_keys = [x for x in model_keys if x not in fnmatch.filter(model_keys, exclude)]

        # Now we have our exact models as list of python module paths from the IOC
        # Now we get actual IOC bindings except our Dict Key is the TABLENAME, not module path
        for model in model_keys:
            tablename = model_bindings[model].object.tablename
            if tablename not in models:
                unsorted_models[tablename] = model_bindings[model]

        # Now we can sort our unsorted_model keys (which are tablenames)
        tablenames = sorted(unsorted_models.keys())

        # Add all sorted models to our final models OrderedDict
        for tablename in tablenames:
            models[tablename] = unsorted_models[tablename]

        return models

    def _get_scopes(self, tablename) -> Dict:
        """Get scopes from options override or default automatic model CRUD scopes"""

        # If custom scopes are passed, add those to every CRUD scope
        # Custom scopes are defined in self.scopes as either a List or Dict
        # If list, apply entire list to all CRUD.  If Dict, only apply to proper CRUD key
        # If scopes is None, no custom scopes are used, so we apply our default model CRUD scopes

        scopes = {}
        scopes['create'] = []
        scopes['read'] = []
        scopes['update'] = []
        scopes['delete'] = []
        scopes['overridden'] = False

        # Note: If you want to ADD other scopes to the automatic model CRUD scopes
        # use a @route.group(scopes=['additional']) instead of the router
        # .include() or .controller() options dict.

        if self.scopes is None:
            # No custom scopes defined, add automatic model CRUD scopes
            scopes['create'].append(tablename + '.create')
            scopes['read'].append(tablename + '.read')
            scopes['update'].append(tablename + '.update')
            scopes['delete'].append(tablename + '.delete')
        else:
            # Custom scopes defined, use these scopes insetead of automatic model CRUD scopes
            scopes['overridden'] = True
            if type(self.scopes) == list:
                # Custom scopes is a list, so apply entire list to each CRUD section
                # Must copy() each list or all will be references to same list
                scopes['create'] = self.scopes.copy()
                scopes['read'] = self.scopes.copy()
                scopes['update'] = self.scopes.copy()
                scopes['delete'] = self.scopes.copy()
            else:
                # Must copy() each list or all will be references to same list
                scopes['create'] = self.scopes.copy().get('create') or []
                scopes['read'] = self.scopes.copy().get('read') or []
                scopes['update'] = self.scopes.copy().get('update') or []
                scopes['delete'] = self.scopes.copy().get('delete') or []
        return scopes
