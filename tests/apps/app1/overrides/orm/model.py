from typing import Any, Dict, Generic, List, Tuple, TypeVar, Union

from pydantic import BaseModel as PydanticBaseModel

import uvicore
from uvicore.contracts import Model as ModelInterface
from uvicore.support.classes import hybridmethod
from uvicore.support.dumper import dd, dump

from uvicore.orm.fields import HasMany
from uvicore.orm.mapper import Mapper
from uvicore.orm.query import QueryBuilder

E = TypeVar("E")

from uvicore.orm.model import Model as X

#class _Model(Generic[E], ModelInterface, PydanticBaseModel):
class Model(X[E]):
#class Model(Generic[E], PydanticBaseModel, metaclass=ModelMetaclass):
#class _Model(PydanticBaseModel):

    @classmethod
    def query(entity) -> QueryBuilder[E]:
        dump('query override----------------------------------')
        return QueryBuilder[entity](entity)

    @classmethod
    def query2(entity):
        return 'query2 here!!!!!!!!!!'
