# Do not import future here or http/bootstrap.py get_type_hints fails
# See https://bugs.python.org/issue41249
# NO from __future__ import annotations

import json
import uvicore
from uvicore.http.request import Request
from uvicore.http.params import Query
from uvicore.typing import Optional, Union, List, Tuple, Generic, TypeVar, Dict
from uvicore.orm.query import OrmQueryBuilder
from uvicore.contracts import AutoApi as AutoApiInterface
from uvicore.support.dumper import dump, dd
from uvicore.http.exceptions import PermissionDenied
from uvicore.contracts import UserInfo
from uvicore.http.exceptions import BadParameter

E = TypeVar("E")

# Default page size and maximum from app config
page_size_default = uvicore.config.app.api.page_size or 25
page_size_max = uvicore.config.app.api.page_size_max or 100


@uvicore.service()
class AutoApi(Generic[E], AutoApiInterface[E]):
    def __init__(self,
        Model: E,
        scopes: List = [],
        *,
        request: Request,
        include: Optional[List[str]] = None,
        find: Optional[str] = None,
        where: Optional[str] = None,
        or_where: Optional[str] = None,
        filter: Optional[str] = None,
        or_filter: Optional[str] = None,
        order_by: Optional[str] = None,
        sort: Optional[str] = None,
        page: Optional[int] = 1,
        page_size: Optional[int] = page_size_default,
    ):
        self.Model = Model
        self.scopes = scopes
        self.request = request
        self.user: UserInfo = request.user
        self.includes = self._build_include(include)
        self.find = self._build_find(find)
        self.page = page
        self.page_size = page_size
        if self.page_size > page_size_max: self.page_size = page_size_max

        # Where and filter JSON look identical, as does the ORM, all considered "whereables"
        self.wheres = self._build_whereable(where)
        self.or_wheres = self._build_whereable(or_where)
        self.filters = self._build_whereable(filter)
        self.or_filters = self._build_whereable(or_filter)

        # Order and sort JSON look identical, as does the ORM, all considered "sortables"
        self.order_bys = self._build_sortable(order_by)
        self.sorts = self._build_sortable(sort)

    @classmethod
    def findsig(
        request: Request,
        id: Union[str, int],
        include: Optional[List[str]] = Query([]),
        filter: Optional[str] = '',
        or_filter: Optional[str] = '',
    ):
        """AutoApi Find Function Signature"""
        pass

    @classmethod
    def getsig(
        request: Request,
        include: Optional[List[str]] = Query([]),
        find: Optional[str] = '',
        where: Optional[str] = '',
        or_where: Optional[str] = '',
        filter: Optional[str] = '',
        or_filter: Optional[str] = '',
        order_by: Optional[str] = '',
        sort: Optional[str] = '',
        page: Optional[int] = 1,
        page_size: Optional[int] = page_size_default,
    ):
        """AutoApi Get Function Signature"""
        pass


    def orm_query(self) -> OrmQueryBuilder[OrmQueryBuilder, E]:
        """Start a new Uvicore ORM Model QueryBuilder Query"""

        # Start empty query builder
        query = self.Model.query()

        # Include
        if self.includes: query.include(*self.includes)

        # Where
        if self.wheres: query.where(self.wheres)

        # OR Where
        if self.or_wheres: query.or_where(self.or_wheres)

        # Filter (children)
        if self.filters: query.filter(self.filters)

        # OR Filter (children)
        if self.or_filters: query.or_filter(self.or_filters)

        # Order by
        if self.order_bys: query.order_by(self.order_bys)

        # Sort (children)
        if self.sorts: query.sort(self.sorts)

        # Page and Page Size (ORM limit and offset)
        query.limit(self.page_size).offset(self.page_size * (self.page - 1))

        #query.key_by('id')

        # Return unfinished, still chainable query builder
        return query

    def guard_relations(self):
        # No includes, skip
        if not self.includes: return self

        # User is superadmin, allow
        if self.user.superadmin: return self

        # Loop each include and parts
        for include in self.includes:

            # Includes are split into dotnotation "parts".  We have to walk down each parts relations
            parts = [include]
            if '.' in include: parts = include.split('.')

            entity = self.Model
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
                model_permissions = [relation.entity.tablename + '.read'] if self.scopes['overridden'] == False else self.scopes['read']
                #dump('CHILD MODEL PERMISSIONS:', model_permissions)

                # User must have ALL scopes defined on the route (an AND statement)
                authorized = True
                missing_scopes = []
                for scope in model_permissions:
                    if scope not in self.user.permissions:
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

        # Chainable
        return self

    def _build_include(self, includes: List):
        if not includes: return
        results = []
        for include in includes:
            if ',' in include:
                results.extend(include.split(','))
            else:
                results.append(include)
        return results

    def _build_find(self, find_str: str) -> Dict:
        if not find_str: return None
        try:
            find = json.loads(find_str)
            if len(find) == 2:
                return {find[0]: find[1]}
        except Exception as e:
            raise BadParameter('Invalid find by named parameter, possibly invalid JSON?', exception=str(e), extra={'params': find_str})

    def _build_whereable(self, where_str: str) -> List[Tuple]:
        if not where_str: return None
        orm_wheres = []
        try:
            # Convert where string JSON to python object only if str, may already be a List from JSON payload not URL
            wheres = json.loads(where_str) if type(where_str) == str else where_str

            # Ensure we have a List[List]
            if type(wheres[0]) != list: wheres = [wheres]

            # Translate JSON object into ORM query builder
            for where in wheres:
                if len(where) == 2:
                    # No operator provided, just field and value, let ORM decide (ORM defaults to =)
                    orm_wheres.append((where[0], where[1]))
                elif len(where) == 3:
                    # Field, Operator and Value provided
                    orm_wheres.append((where[0], where[1], where[2]))

            return orm_wheres
        except Exception as e:
            raise BadParameter('Invalid where/or_where/filter/or_filter parameter, possibly invalid JSON?', exception=str(e), extra={'params': where_str})

    def _build_sortable(self, order_by_str: str) -> List[Tuple]:
        if not order_by_str: return None
        orm_order_bys = []
        try:
            # A simple order_by does not need to be json, could be ?order_by=id  If so, convert it to string [] list
            if order_by_str[0] != '[': order_by_str = '["' + order_by_str + '"]'

            # Convert order string JSON to python object only if str, may already be a List from JSON payload not URL
            order_bys = json.loads(order_by_str) if type(order_by_str) == str else order_by_str

            # Ensure we have a List[List]
            if type(order_bys[0]) != list: order_bys = [order_bys]

            # Translate JSON object into ORM query builder
            for order_by in order_bys:
                if len(order_by) == 1:
                    # No 'DESC' or 'ASC' defined, let ORM decide (ORM defaults to ASC)
                    orm_order_bys.append((order_by[0]))
                elif len(order_by) == 2:
                    # Both field and order (DESC, ASC) provided
                    orm_order_bys.append((order_by[0], order_by[1]))

            return orm_order_bys
        except Exception as e:
            raise BadParameter('Invalid order_by parameter, possibly invalid JSON?', exception=str(e), extra={'params': order_by_str})

