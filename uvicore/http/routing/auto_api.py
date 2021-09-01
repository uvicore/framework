# Do not import future here or http/bootstrap.py get_type_hints fails
# See https://bugs.python.org/issue41249
# NO from __future__ import annotations

import uvicore
import json
from uvicore.http.request import Request
from uvicore.http.params import Query
from uvicore.typing import Optional, Union, List, Any, Tuple, Generic, TypeVar
from uvicore.orm.query import OrmQueryBuilder
from uvicore.contracts import AutoApi as AutoApiInterface
from uvicore.support.dumper import dump, dd
from uvicore.http.exceptions import PermissionDenied

E = TypeVar("E")

@uvicore.service()
class AutoApi(Generic[E], AutoApiInterface[E]):
    def __init__(self,
        Model: E,
        scopes: List = [],
        *,
        request: Request,
        include: Optional[List[str]] = None,
        where: Optional[str] = None
    ):
        self.Model = Model
        self.scopes = scopes
        self.request = request
        self.user: UserInfo = request.user
        self.includes = self._build_include(include)
        self.wheres = self._build_where(where)

    @classmethod
    def listsig(
        request: Request,
        include: Optional[List[str]] = Query([]),
        where: Optional[str] = '',
    ):
        pass

    @classmethod
    def getsig(
        request: Request,
        id: Union[str, int],
        include: Optional[List[str]] = Query([]),
    ):
        pass

    """
    A URL is a ONE-TO-ONE mapping to an ORM QUERY
    ---------------------------------------------

    HTTP: DELETE /api/posts?where={"creator_id":"1"} // mabe 500 posts
    ORM: Post.query().where('creator_id', 1).delete()
    SQL: DELETE FROM posts WHERE creator_id=1;

    HTTP: PATCH /api/posts?where={"creator_id":"1"}
    BODY would be the columns to update
        {
            'creator_id': 12
            'owner_id': 5
        }
    ORM: Post.query().where('creator_id', 1).update('creator_id', 12).update('owner_id', 5)
    SQL: UPDATE posts SET creator_id=12, owner_id=4 WHERE creator_id=1;
    """


    def orm_query(self) -> OrmQueryBuilder[OrmQueryBuilder, E]:
        """Start a new Uvicore ORM Model QueryBuilder Query"""
        query = self.Model.query()

        # Include
        #if include: query.include(*include.split(','))
        if self.includes: query.include(*self.includes)

        # Where
        if self.wheres: query.where(self.wheres)
        #dump(query.query)

        return query

    def guard_relations(self):
        # No includes, skip
        if not self.includes: return self

        # User is superadmin, allow
        #if self.user.superadmin: return self

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
        results = []
        for include in includes:
            if ',' in include:
                results.extend(include.split(','))
            else:
                results.append(include)
        return results

    def _build_where(self, where_str: str) -> List[Tuple]:
        wheres = []
        if not where_str: return wheres
        try:
            # Convert where string JSON to python object
            where_json = json.loads(where_str)

            # Where must be a dict
            if not isinstance(where_json, dict): return

            # WORKS - where={"id": [">", 5]}
            # WORKS - where={"id": ["in", [1, 2, 3]]}
            # WORKS - where={"title": ["like", "%black%"]}
            # WORKS - where={"id": 65, "topic_id": ["in", [1, 2, 3, 4, 5]]}
            # WORKS - ?include=topic.section.space&where={"topic.slug": "/tools", "topic.section.slug": "/apps", "topic.section.space.slug": "/dev"}

            for (key, value) in where_json.items():
                #dump("Key: " + str(key) + " - Value: " + str(value))
                if isinstance(value, List):
                    if len(value) != 2: continue  # Valid advanced value must be 2 item List
                    operator = value[0]
                    value = value[1]
                    #query.where(key, operator, value)
                    wheres.append((key, operator, value))
                else:
                    #query.where(key, value)
                    wheres.append((key, '=', value))
            return wheres
        except Exception as e:
            #self.log.error(e)
            dump(e)

