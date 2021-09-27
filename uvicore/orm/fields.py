from __future__ import annotations
import uvicore
import sqlalchemy as sa
from dataclasses import dataclass
from uvicore.support import module
from uvicore.support.dumper import dd, dump
from uvicore.contracts import Field as FieldInterface
from uvicore.contracts import Relation as RelationInterface
from typing import Any, Callable, Dict, Optional, OrderedDict

# NOTE dataclass required on each on THAT HAS PROPERTIES event hough they all
# impliment Relation.  If a class does not have property overrides, then do NOT add @dataclass


@dataclass
@uvicore.service()
class Relation(RelationInterface):
    # __slots__ = (
    #     'model',
    #     'foreign_key',
    #     'local_key',
    #     'name',
    #     'entity',
    # )

    # By setting a default on these attributes of a dataclass
    # When printed, only the ones actually set will show up, which makes output much smaller
    model: str
    foreign_key: Optional[str] = None
    local_key: Optional[str] = None
    name: Optional[str] = None
    entity: Optional[Any] = None

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

    def fill(self, field: Field) -> Relation:
        if not self.foreign_key:
            self.foreign_key = 'id'
        if not self.local_key:
            self.local_key = str(field.name) + '_id'
        self.name = field.name
        self._load_entity()
        return self

    def _fill_reverse(self, field: Field) -> Relation:
        if not self.foreign_key:
            self.foreign_key = str(field.name) + '_id'
        if not self.local_key:
            self.local_key = 'id'
        self.name = field.name
        self._load_entity()
        return self

    def is_one(self) -> bool:
        return type(self) == HasOne or type(self) == BelongsTo or type(self) == MorphOne

    def is_many(self) -> bool:
        return type(self) == HasMany or type(self) == BelongsToMany or type(self) == MorphMany or type(self) == MorphToMany

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
            if relation_type == HasMany or relation_type == BelongsToMany or relation_type == MorphMany or relation_type == MorphToMany:
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
class HasOne(Relation):
    """One-To-One Relationship"""

    # In a HasOne, the foreign_key is required since I don't know
    # the name of the current model, so this __init__ override simply
    # makes foreign_key required
    def __init__(self,
        model: str,
        *,
        foreign_key: str,
        local_key: str = None,
    ) -> None:
        super().__init__(model, foreign_key=foreign_key, local_key=local_key)

    # HasOne is also reversed in how it deduces the optional local_key, its just id
    def fill(self, field: Field) -> Relation:
        return self._fill_reverse(field)


@uvicore.service()
class HasMany(Relation):
    """One-To-Many Relationship"""

    # For a HasMany the foreign_key is required
    def __init__(self,
        model: str,
        *,
        foreign_key: str,
        local_key: str = None,
    ) -> None:
        super().__init__(model, foreign_key=foreign_key, local_key=local_key)

    def fill(self, field: Field) -> Relation:
        return self._fill_reverse(field)


@uvicore.service()
class BelongsTo(Relation):
    """Inverse of One-To-One or One-To-Many Relationship"""
    pass


@dataclass
@uvicore.service()
class BelongsToMany(Relation):
    """Many-To-Many Relationship (Both Sides)

    :param model: Related model as import string
    :param join_tablename: Table name of join/intermediate/pivot table
    :param left_key: The foreign key column of the model on which you are defining the relationship
    :param right_key: The foreign key column of the model that you are joining to
    """
    model: str
    join_tablename: str = None
    left_key: str = None
    right_key: str = None
    name: Optional[str] = None
    entity: Optional[Any] = None
    join_table: Optional[sa.Table] = None

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


@dataclass
@uvicore.service()
class Morph(Relation):
    model: str
    polyfix: str = None
    foreign_type: Optional[str] = None
    foreign_key: Optional[str] = None
    local_key: Optional[str] = None
    dict_key: Optional[str] = None
    dict_value: Optional[str] = None
    list_value: Optional[str] = None
    name: Optional[str] = None
    entity: Optional[Any] = None

    def __init__(self,
        model: str,
        polyfix: str = None,
        *,
        foreign_type: str = None,
        foreign_key: str = None,
        local_key: str = None,
        dict_key: str = None,
        dict_value: str = None,
        list_value: str = None,
    ) -> None:
        self.model = model
        self.polyfix = polyfix
        self.foreign_type = foreign_type or polyfix + '_type'
        self.foreign_key = foreign_key or polyfix + '_id'
        self.local_key = local_key or 'id'
        self.dict_key = dict_key
        self.dict_value = dict_value
        self.list_value = list_value

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


@dataclass
@uvicore.service()
class MorphToMany(Morph):
    model: str
    join_tablename: str = None
    polyfix: str = None
    right_key: str = None
    left_type: Optional[str] = None
    left_key: Optional[str] = None
    dict_key: Optional[str] = None
    dict_value: Optional[str] = None
    list_value: Optional[str] = None
    name: Optional[str] = None
    entity: Optional[Any] = None
    join_table: Optional[sa.Table] = None

    def __init__(self,
        model: str,
        *,
        join_tablename: str,
        polyfix: str,
        right_key: str,
        left_type: str = None,
        left_key: str = None,
        dict_key: str = None,
        dict_value: str = None,
        list_value: str = None,
    ) -> None:
        self.model = model
        self.join_tablename = join_tablename
        self.polyfix = polyfix
        self.right_key = right_key
        self.left_type = left_type or polyfix + '_type'
        self.left_key = left_key or polyfix + '_id'

        # Dict key/value for MorphToMany has NOT yet been implimented
        self.dict_key = dict_key
        self.dict_value = dict_value
        self.list_value = list_value

        # Set by self.fill later
        self.name = None
        self.entity = None
        self.join_table = None

    def fill(self, field: Field):
        # Fill in parameters
        self.name = field.name

        # Load entity
        self._load_entity()

        # Get actual SQLAlchemy relation table
        self.join_table = uvicore.db.table(self.join_tablename, self.entity.connection)
        return self



# Relationship Aliases
# At one point I thought I would make aliases to help other write as OneToOne...
# But this will complicate things and doesn't actually make things any easier
# to read or understand.  Especially because BelongsTo works for ManyToOne and
# also for the inverse side of a OneToOne which I don't have a name for, maybe
# OneToOneInverse = BelongsTo?

# OneToOne        = HasOne
# OneToOneInverse = BelongsTo
# OneToMany       = HasMany
# ManyToOne       = BelongsTo
# ManyToMany      = BelongsToMany
# OneToOneMorph   = MorphOne
# OneToManyMorph  = MorphMany
# ManyToManyMorph = MorphToMany




@dataclass
@uvicore.service()
class Field(FieldInterface):
    column: str
    name: Optional[str] = None
    primary: Optional[bool] = False
    title: Optional[str] = None
    description: Optional[str] = None
    default: Optional[Any] = None
    sortable: Optional[bool] = None
    searchable: Optional[bool] = None
    read_only: Optional[bool] = None
    write_only: Optional[bool] = None
    callback: Optional[Any] = None
    evaluate: Optional[Callable] = None
    relation: Optional[Relation] = None
    json: Optional[bool] = False
    properties: Optional[Dict] = None

    min_length: Optional[int] = None
    max_length: Optional[int] = None
    example: Optional[Any] = None


    # Of all the uvicore Field() arguments, these are VALID OpenAPI fields and handled properly by Pydantic FieldInfo()
    # See pydantic/fields.py def field() or class FieldInfo() for their params.
    # Note that 'required' is not part of FieldInfo but part of pydantics ModelInfo which is automatically
    # handled by the Optional typehinting on the field type.
    # See https://swagger.io/docs/specification/data-models/keywords/ for all valid schema keywords
    # Run your final .json schema through https://apitools.dev/swagger-parser/online/ to validate
    __valid_oepnapi_keywords__ = [
        'title',
        'description',
        'default',
        #'required',
        'example',

        # These get converted to camelCase in metaclass.py for OpenAPI compatibility
        'read_only',
        'write_only',
        'min_length',
        'max_length',
    ]

    # These uvicore Field() arguments will be converted to the x-tra Dict "specification extensions".
    # See https://swagger.io/specification/#specification-extensions
    __convert_to_extensions__ = [
        #'column',
        'sortable',
        'searchable',
        'properties',
    ]

    def __init__(self, column: str = None, *,
        name: Optional[str] = None,
        primary: Optional[bool] = False,
        title: Optional[str] = None,
        description: Optional[str] = None,
        default: Optional[Any] = None,
        #required: Optional[bool] = False,
        sortable: Optional[bool] = None,  # Must be none if not set to hide in OpenAPI
        searchable: Optional[bool] = None,  # Must be none if not set to hide in OpenAPI
        read_only: Optional[bool] = None,  # Must be none if not set to hide in OpenAPI
        write_only: Optional[bool] = None,  # Must be none if not set to hide in OpenAPI
        callback: Optional[Any] = None,
        evaluate: Optional[Callable] = None,
        relation: Optional[Relation] = None,
        json: Optional[bool] = False,
        properties: Optional[Dict] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        example: Optional[Any] = None,
    ):
        self.column = column
        self.name = name
        self.primary = primary
        self.title = title
        self.description = description
        self.default = default
        #self.required = required
        self.sortable = sortable
        self.searchable = searchable
        self.read_only = read_only
        self.write_only = write_only
        self.callback = callback
        self.evaluate = evaluate
        self.relation = relation
        self.json = json
        self.properties = properties
        self.min_length = min_length
        self.max_length = max_length
        self.example = example
