from __future__ import annotations
import uvicore
from typing import Dict, Tuple, Any, Optional, Callable, OrderedDict
from pydantic.fields import FieldInfo
from pydantic.utils import Representation
from uvicore.support import module
from uvicore.support.dumper import dump, dd
from uvicore.contracts import Relation as RelationInterface
from uvicore.contracts import Field as FieldInterface


@uvicore.service()
class _Relation(RelationInterface, Representation):
    __slots__ = (
        'model',
        'foreign_key',
        'local_key',
        'name',
        'entity',
    )

    def __init__(self,
        model: str,
        *,
        foreign_key: str = None,
        local_key: str = None,
    ) -> None:
        self.model = model
        self.foreign_key = foreign_key
        self.local_key = local_key

        # Set by self.fill later
        self.name = None
        self.entity = None

    def fill(self, field: Field) -> _Relation:
        if not self.foreign_key:
            self.foreign_key = 'id'
        if not self.local_key:
            self.local_key = str(field.name) + '_id'
        self.name = field.name
        self._load_entity()
        return self

    def _fill_reverse(self, field: Field) -> _Relation:
        if not self.foreign_key:
            self.foreign_key = str(field.name) + '_id'
        if not self.local_key:
            self.local_key = 'id'
        self.name = field.name
        self._load_entity()
        return self

    def is_one(self) -> bool:
        return type(self) == HasOne or type(self) == MorphOne or type(self) == BelongsTo

    def is_many(self) -> bool:
        return type(self) == HasMany or type(self) == MorphMany or type(self) == BelongsToMany

    def is_type(self, *args) -> bool:
        for arg in args:
            if type(self) == arg:
                return True
        return False

    def contains_many(self, relations: OrderedDict, skip: List = []) -> bool:
        """Walk down all sub_relations by __ name and check if any are *Many"""
        walk = ''
        sub_relations = self.name.split('__')
        i = 0
        for sub_relation in sub_relations:
            # Walk down by concatenation
            walk += sub_relation

            # Skip these sub_relations if desired
            if len(skip) > i and skip[i] == sub_relation:
                walk += '__'
                i += 1
                continue

            # Check relation type for *Many
            relation_type = type(relations.get(walk))
            if relation_type == HasMany or relation_type == MorphMany or relation_type == BelongsToMany:
                return True

            # Walk down
            walk += '__'
            i += 1
        return False

    def _load_entity(self):
        # Fill actual entity class
        if uvicore.ioc.binding(self.model):
            self.entity = uvicore.ioc.make(self.model)
        else:
            self.entity = module.load(self.model).object


@uvicore.service()
class HasOne(_Relation):
    """One-To-One Relationship"""
    def fill(self, field: Field) -> _Relation:
        return self._fill_reverse(field)


@uvicore.service()
class HasMany(_Relation):
    """One-To-Many Relationship"""
    def fill(self, field: Field) -> _Relation:
        return self._fill_reverse(field)


@uvicore.service()
class BelongsTo(_Relation):
    """Inverse of One-To-One or One-To-Many Relationship"""
    pass


@uvicore.service()
class BelongsToMany(_Relation):
    """Many-To-Many Relationship (Both Sides)

    :param model: Related model as import string
    :param join_tablename: Table name of join/intermediate/pivot table
    :param left_key: The foreign key column of the model on which you are defining the relationship
    :param right_key: The foreign key column of the model that you are joining to
    """

    __slots__ = (
        'model',
        'join_tablename',
        'left_key',
        'right_key',
        'name',
        'entity',
        'join_table',
    )

    def __init__(self,
        model: str,
        *,
        join_tablename: str,
        left_key: str,
        right_key: str,
    ) -> None:
        self.model = model
        self.join_tablename = join_tablename
        self.left_key = left_key
        self.right_key = right_key

        # Set by self.fill later
        self.name = None
        self.entity = None
        self.join_table = None
        # The left_key is the foreign key name of the model on which you are defining the relationship
        # The right_key is the foreign key name of the model that you are joining to

    def fill(self, field: Field):
        """Fill in additional instance variables like entity and join_table

        :param field: The model field that holds this relation
        """
        # Fill in parameters
        self.name = field.name

        # Load entity
        self._load_entity()

        # Get actual SQLAlchemy relation table
        self.join_table = uvicore.db.table(self.join_tablename, self.entity.connection)
        return self


@uvicore.service()
class Morph(_Relation):
    __slots__ = (
        'model',
        'polyfix',
        'foreign_type',
        'foreign_key',
        'local_key',
        'dict_key',
        'dict_value',
        'name',
        'entity',
    )

    def __init__(self,
        model: str,
        *,
        polyfix: str = None,
        foreign_type: str = None,
        foreign_key: str = None,
        local_key: str = None,
        dict_key: str = None,
        dict_value: str = None,
    ) -> None:
        self.model = model
        self.polyfix = polyfix
        self.foreign_type = foreign_type or polyfix + '_type'
        self.foreign_key = foreign_key or polyfix + '_id'
        self.local_key = local_key or 'id'
        self.dict_key = dict_key
        self.dict_value = dict_value

        # Set by self.fill later
        self.name = None
        self.entity = None

    def fill(self, field: Field):
        self.name = field.name
        self._load_entity()
        return self


@uvicore.service()
class MorphOne(Morph):
    pass


@uvicore.service()
class MorphMany(Morph):
    pass



# class MorphTo(Relation):

#     def __init__(self):
#         pass


@uvicore.service()
class Field(FieldInterface, Representation):

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
        'json',
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
        relation: Optional[_Relation] = None,
        json: Optional[bool] = False,
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
        self.json = json
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
