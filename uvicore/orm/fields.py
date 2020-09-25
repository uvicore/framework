import uvicore
from typing import Dict, Tuple, Any, Optional, Callable
from pydantic.fields import FieldInfo
from pydantic.utils import Representation
from uvicore.support import module
from uvicore.support.dumper import dump, dd

class Relation(Representation):
    __slots__ = (
        'model',
        'foreign_key',
        'local_key',
        'name',
        'entity',
    )

    def __init__(self,
        model: str,
        foreign_key: str = None,
        local_key: str = None,
    ) -> None:
        self.model = model
        self.foreign_key = foreign_key
        self.local_key = local_key
        self.name = None
        self.entity = None

    def fill(self, field: 'Field'):
        if not self.foreign_key:
            self.foreign_key = 'id'
        if not self.local_key:
            self.local_key = str(field.name) + '_id'
        self.name = field.name
        self._load_entity()
        return self

    def _fill_reverse(self, field: 'Field'):
        if not self.foreign_key:
            self.foreign_key = str(field.name) + '_id'
        if not self.local_key:
            self.local_key = 'id'
        self.name = field.name
        self._load_entity()
        return self

    def _load_entity(self):
        # Fill actual entity class
        if uvicore.ioc.binding(self.model):
            self.entity = uvicore.ioc.make(self.model)
        else:
            self.entity = module.load(self.model).object




class BelongsToMany(Representation):
    __slots__ = (
        'model',
        'join_table',
        'local_key',
        'foreign_key',
    )

    def __init__(self,
        model: str,
        join_table: str,
        local_key: str,
        foreign_key: str,
    ) -> None:
        self.model = model
        self.join_table = join_table
        self.local_key = local_key
        self.foreign_key = foreign_key

    def fill(self, field: 'Field'):
        pass


class HasOne(Relation):
    def fill(self, field: 'Field'):
        return self._fill_reverse(field)

class HasMany(Relation):
    def fill(self, field: 'Field'):
        return self._fill_reverse(field)

class BelongsTo(Relation):
    pass


class Field(Representation):

    # Required for pretty Representaion
    __slots__ = (
        'column',
        'name',
        'primary',
        'title',
        'description',
        'default',
        'required',
        'sortable',
        'searchable',
        'read_only',
        'write_only',
        'callback',
        'relation',
        'properties'
    )

    def __init__(self, column: str = None, *,
        name: Optional[str] = None,
        primary: Optional[bool] = False,
        title: Optional[str] = None,
        description: Optional[str] = None,
        default: Optional[Any] = None,
        required: Optional[bool] = False,
        sortable: Optional[bool] = None,  # Must be none if not set to hide in OpenAPI
        searchable: Optional[bool] = None,  # Must be none if not set to hide in OpenAPI
        read_only: Optional[bool] = None,  # Must be none if not set to hide in OpenAPI
        write_only: Optional[bool] = None,  # Must be none if not set to hide in OpenAPI
        callback: Optional[Any] = None,
        relation: Optional[Relation] = None,
        properties: Optional[Dict] = None,
    ):
        self.column = column
        self.name = name
        self.primary = primary
        self.title = title
        self.description = description
        self.default = default
        self.required = required
        self.sortable = sortable
        self.searchable = searchable
        self.read_only = read_only
        self.write_only = write_only
        self.callback = callback
        self.relation = relation
        self.properties = properties


# class PydanticField(FieldInfo):

#     def __init__(self, column: str = None, *,
#         primary: Optional[bool] = False,
#         title: Optional[str] = None,
#         description: Optional[str] = None,
#         default: Optional[Any] = None,
#         required: bool = False,
#         sortable: bool = False,
#         searchable: bool = False,
#         read_only: Optional[bool] = None,
#         write_only: Optional[bool] = None,
#         callback: Optional[Any] = None,
#         has_one: Optional[Tuple] = None,
#         has_many: Optional[Tuple] = None,
#         belongs_to: Optional[Tuple] = None,
#         properties: Optional[Dict] = None,
#     ):
#         self.column = column
#         self.primary = primary
#         self.title = title
#         self.description = description
#         self.default = default
#         self.required = required
#         self.sortable = sortable
#         self.searchable = searchable
#         self.read_only = read_only
#         self.write_only = write_only
#         self.callback = callback
#         self.has_one = has_one
#         self.has_many = has_many
#         self.belongs_to = belongs_to
#         self.properties = properties
#         super().__init__(
#             default=default,
#             column=column,
#             primary=primary,
#             title=title,
#             description=description,
#             required=required,
#             sortable=sortable,
#             searchable=searchable,
#             readOnly=read_only,
#             writeOnly=write_only,
#             callback=callback,
#             has_one=has_one,
#             has_many=has_many,
#             belongs_to=belongs_to,
#             properties=properties,
#         )
