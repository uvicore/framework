import uvicore
import inspect
import fnmatch
from uvicore.typing import Optional, List, Tuple, Dict, Any, OrderedDict, Union
from uvicore.http.routing.api_router import ApiRouter
from uvicore.http.routing.router import Routes as Controller
from uvicore.http.request import Request
from uvicore.http.response import JSON
from uvicore.support import str as string
from uvicore.support.dumper import dump, dd
from uvicore.support import module
from uvicore.http.exceptions import HTTPException, NotFound
from uvicore.contracts import UserInfo
from uvicore.http.routing import Guard
from uvicore.orm import Model as OrmModel
from uvicore.http.routing.auto_api import AutoApi
from uvicore.support.collection import setvalue
from pydantic import BaseModel as PydanticModel
from pydantic import BaseModel

from starlette.responses import JSONResponse

# -where
# -or_where
# -filter
# -or_filter
# -order_by
# -sort
# -page and page_size - in vue and uvicore orm these are actually done with limit() and offset()
# Add a find for named finds still returning one


# key_by
# cache
# show_writeonly


class HTTPMessage(BaseModel):
  #status_code: int
  message: str
  #detail: Optional[str]
  #extra: Optional[Dict]


class DeleteQuery(PydanticModel):
    where: Optional[dict[str, Union[str, List]]]

    class Config:
        schema_extra = {
            "example": {
                "where": {
                    "creator_id": 1,
                    "title": ["in", ["title1", "title2"]],
                    "body": ["like", "%delete me%"],
                },
            }
        }

@uvicore.service()
class ModelRoutes:
    """Dynamic Model CRUD Routes"""

    @property
    def log(self):
        return uvicore.log.name('uvicore.model_router')

    def register(self, Model: OrmModel, route: ApiRouter, path: str, tags: List, scopes: List):
        """Build dynamic model CRUD routes"""

        #@route.get('/' + path, inherits=AutoApi.getsig, response_model=List[Model], tags=tags, scopes=[Model.tablename + '.read'] if scopes is None else scopes)
        @route.get(
            path='/' + path,
            inherits=AutoApi.getsig,
            response_model=Union[List[Model], Model, Dict],
            tags=tags,
            scopes=scopes['read'],
            summary="List multiple {}".format(Model.tablename),
            description="List one or more {} ({}) using the optional filtering parameters.".format(Model.tablename, Model.modelfqn),
        )
        async def get_all(**kwargs):
            api = AutoApi(Model, scopes, **kwargs).guard_relations()
            query = api.orm_query()

            # Run ORM query for results
            try:
                if api.find:
                    results = await query.find(**api.find)
                else:
                    results = await query.get()
                return results
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail="Error in query builder, most likely an unknown column or query parameter.",
                    exception=str(e)
                )

        @route.get(
            path='/' + path + '/{id}',
            inherits=AutoApi.findsig,
            # responses={
            #     404: {
            #         'model': HTTPMessage,
            #         #'description': 'xyz here',
            #         #'content': {"application/json": HTTPMessage},
            #     },
            # },
            response_model=Model,
            tags=tags,
            scopes=scopes['read'],
            summary="Get one {} by primary key".format(Model.tablename),
            description="Get a single {} ({}) by primary key.".format(Model.tablename, Model.modelfqn),
        )
        async def find_one(id: Union[str,int], **kwargs):
            api = AutoApi(Model, scopes, **kwargs).guard_relations()
            query = api.orm_query()

            # Run ORM query for results
            try:
                results = await query.find(id)
            except:
                raise HTTPException(500, str("Error in query builder, most likely an unknown column or query parameter."))

            if results:
                return results
            else:
                #raise NotFound()
                return JSONResponse(status_code=404, content={"message": "Item not found"})


        @route.post(
            path='/' + path,
            response_model=Union[Model, List[Model]],
            tags=tags,
            scopes=scopes['create'],
            summary="Create new {}".format(Model.tablename),
            description="Create one or more {} ({}) without nested relations by POSTING a valid and complete Model.".format(Model.tablename, Model.modelfqn),
        )
        #async def post(request: Request, item: Model):
        async def create(request: Request, items: Union[Model, List[Model]]):
            # NOTES
            # How do I check each child relations permissions, there is no includes
            # Would have to flip each item key and check if its a relation?
            # Then check if user has access to that relation?

            # Insert into storage and return primary key inserted
            try:
                # Ensure list
                is_single = False
                if type(items) != list:
                    items = [items]
                    is_single = True

                for item in items:
                    pk = await Model.insert(item)

                    # If primary key is read_only, assume its an auto-incrementing pk
                    # If not read_only, its a manual pk like 'key'.
                    # Only set new pk result if pk is read_only.  Why? Because when pk is 'key'
                    # a string, encode/databases does not return the new pk, just returns 1 every time.
                    if Model.modelfield(Model.pk).read_only == True:
                        setvalue(item, Model.pk, pk)

                # Return inserted item
                if is_single:
                    return items[0]
                else:
                    return items

            except Exception as e:
                raise HTTPException(500, str(e))


        @route.post(
            path='/' + path + '/with_relations',
            response_model=Union[Dict, List[Dict]],
            tags=tags,
            scopes=scopes['create'],
            summary="Create new {} with nested relations".format(Model.tablename),
            description="Create one or more {} ({}) with deeply nested relations by POSTING an object/array.  Uvicore must disable model validation when passing a complex nested relational object.  It is therefore up to you to ensure an accurate object is passed.".format(Model.tablename, Model.modelfqn),
        )
        async def create_with_relations(request: Request, items: Union[Dict, List[Dict]]):
            # NOTES
            # How do I check each child relations permissions, there is no includes
            # Would have to flip each item key and check if its a relation?
            # Then check if user has access to that relation?

            # Insert into storage and return primary key inserted
            try:
                # Ensure list
                is_single = False
                if type(items) != list:
                    items = [items]
                    is_single = True

                for item in items:
                    pk = await Model.insert_with_relations(item.copy())

                    # If primary key is read_only, assume its an auto-incrementing pk
                    # If not read_only, its a manual pk like 'key'.
                    # Only set new pk result if pk is read_only.  Why? Because when pk is 'key'
                    # a string, encode/databases does not return the new pk, just returns 1 every time.
                    if Model.modelfield(Model.pk).read_only == True:
                        setvalue(item, Model.pk, pk)

                # Return inserted items
                #dump(item)
                if is_single:
                    return items[0]
                else:
                    return items

            except Exception as e:
                raise HTTPException(500, str(e))


        @route.put(
            path='/' + path + '/{id}',
            response_model=Model,
            tags=tags,
            scopes=scopes['update'],
            summary="Update one complete {} by primary key".format(Model.tablename),
            description="Update a single {} ({}) by primary key by PUTTING a valid and complete Model.".format(Model.tablename, Model.modelfqn),
        )
        async def update_one(request: Request, id: Union[str,int], item: Model):
            # PUT is used to UPDATE an EXISTNIG record.
            # The PUT object must be a complete object. This is why 'item' is a Model, not a Dict
            try:
                result = await Model.query().find(id)
            except Exception as e:
                raise HTTPException(500, str(e))

            if result:
                # PUT requires a complete item.  It is not partial, it is not merged like a PATCH
                # So we take the entire "item" and simply use the PK from results to update the right record
                setattr(item, Model.pk, getattr(result, Model.pk))
                try:
                    await item.save()
                    return item
                except Exception as e:
                    raise HTTPException(500, str(e))
            else:
                raise NotFound('{} {} not found'.format(Model.modelname, id))


        @route.patch(
            path='/' + path + '/{id}',
            response_model=Model,
            tags=tags,
            scopes=scopes['update'],
            summary="Update one partial {} by primary key".format(Model.tablename),
            description="Update a single {} ({}) by primary key by PATCHING a partial object.  All fields in the object are optional.".format(Model.tablename, Model.modelfqn),
        )
        async def update_one_partial(request: Request, id: Union[str,int], item: Dict):
            # PATCH is used to UPDATE an EXISTNIG record.
            # The PATCH may be a partial object as it is merged with the existing object before being saved.
            # This is why 'item' must be a Dict, not a Model as pydantic would complain about missing fields.
            # All fields in a PATCH are optional.
            try:
                result = await Model.query().find(id)
            except Exception as e:
                raise HTTPException(500, str(e))

            if result:
                # PUT requires a complete item.  It is not partial, it is not merged like a PATCH
                # So we take the entire "item" and simply use the PK from results to update the right record
                for (key, value) in item.items():
                    setattr(result, key, value)
                try:
                    await result.save()
                    return result
                except Exception as e:
                    raise HTTPException(500, str(e))
            else:
                raise NotFound('{} {} not found'.format(Model.modelname, id))




        @route.delete(
            path='/' + path + '/{id}',
            # responses={
            #     404: {
            #         'model': HTTPMessage,
            #         'description': 'xyz here'
            #     },
            # },
            response_model=Model,
            tags=tags,
            scopes=scopes['delete'],
            summary="Delete one {} by primary key".format(Model.tablename),
            description="Delete a single {} ({}) by primary key.".format(Model.tablename, Model.modelfqn),
        )
        async def delete_one(request: Request, id: Union[str,int]):
            # DELETE must act on a single resource ONLY /{id}.  It does NOT take a body/paylad at all.
            # If you want to BULK delete using a body/payload with a JSON query, use POST instead with
            # a new custom endpoint like POST /users/delete payload={"where": ...}
            try:
                result = await Model.query().find(id)
            except Exception as e:
                raise HTTPException(500, str(e))

            if result:
                #await result.unlink('tags')
                await result.delete()
                return result
            else:
                raise NotFound('{} {} not found'.format(Model.modelname, id))
                #return JSON(status_code=404, content={"message": "asdf"})

        # NO, not RESTful.  DELETE does NOT take a body/payload
        # Instead, if you want bulk deletes, create a POST /users/delete with a payload query
        # @route.delete(
        #     path='/' + path,
        #     response_model=Model,
        #     tags=tags,
        #     scopes=scopes['delete'],
        #     summary="Delete {} using a query".format(Model.tablename),
        #     description="Delete one or more {} ({}) using a query.".format(Model.tablename, Model.modelfqn),
        # )
        # async def delete_many(request: Request, query: DeleteQuery):
        #     # PATCH is used to UPDATE an EXISTNIG record.
        #     # The PATCH may be a partial object as it is merged with the existing object before being saved.
        #     # This is why 'item' must be a Dict, not a Model as pydantic would complain about missing fields.
        #     # All fields in a PATCH are optional.
        #     try:
        #         dump(query, query.where)
        #         api = AutoApi(Model, scopes, request=request, where=query.where)
        #         q = api.orm_query()
        #         dump(q.query)

        #         results = await q.delete()
        #         dump(results)
        #         #return results


        #         #result = await Model.query().find(id)
        #         #await result.unlink('tags')
        #         #await result.delete()
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
