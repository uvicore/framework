import uvicore
from typing import Any, Dict
from pydantic import BaseModel as PydanticBaseModel
from uvicore.contracts import Model as ModelInterface
from uvicore.support.dumper import dd, dump


class _Model(ModelInterface, PydanticBaseModel):

    def __init__(self, **data: Any) -> None:
        # Call pydantic parent
        super().__init__(**data)

        # Fill in callback properties
        for (key, callback) in self.__class__.__callbacks__.items():
            setattr(self, key, callback(self))

    async def save(self):
        """Save this model to the database"""
        table = self.__table__
        values = self._to_table()
        query = table.insert().values(**values)
        await self._execute(query)

    async def delete(self):
        """Delete this model from the database"""
        pass

    def _to_table(self) -> Dict:
        """Convert an model entry into a dictionary matching the tables columns"""
        table_columns = {}
        for (key, value) in self.__dict__.items():
            field = self.__class__.__fields__.get(key)
            extra = field.field_info.extra
            column_name = extra.get('column')
            if column_name and not extra.get('readOnly'):
                table_columns[column_name] = value
        return table_columns


# IoC Class Instance
Model: ModelInterface = uvicore.ioc.make('Model')

# Public API for import * and doc gens
__all__ = ['_Model', 'Model']
