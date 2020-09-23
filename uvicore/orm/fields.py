from typing import Dict, Tuple, Any, Optional, Callable
from pydantic.fields import FieldInfo
from pydantic.utils import Representation



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
            self.local_key = field.name + '_id'

    def _fill_reverse(self, field: 'Field'):
        if not self.foreign_key:
            self.foreign_key = field.name + '_id'
        if not self.local_key:
            self.local_key = 'id'



class HasOne(Relation):
    def fill(self, field: 'Field'):
        self._fill_reverse(field)

class HasMany(Relation):
    def fill(self, field: 'Field'):
        self._fill_reverse(field)

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
        'has_one',
        'has_many',
        'belongs_to',
        'relation',
        'properties'
    )

    def __init__(self, column: str = None, *,
        name: Optional[bool] = False,
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
        has_one: Optional[Tuple] = None,
        has_many: Optional[Tuple] = None,
        belongs_to: Optional[Tuple] = None,
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
        self.has_one = has_one
        self.has_many = has_many
        self.belongs_to = belongs_to
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
