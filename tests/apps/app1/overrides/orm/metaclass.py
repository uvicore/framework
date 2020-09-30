from typing import Any
from uvicore.support.dumper import dd, dump
from uvicore.orm.query import QueryBuilder

# Parent
from uvicore.orm.metaclass import ModelMetaclass as X

class ModelMetaclass(X):

    async def find(entity, id: Any) -> Any:
        """Query builder passthrough"""
        dump('find override----------------------------------')
        return await QueryBuilder(entity).find(id)
