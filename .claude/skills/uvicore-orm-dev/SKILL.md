---
name: uvicore-orm-dev
description: "Working on the Uvicore ORM internals under uvicore/orm/ — Model, ModelMetaclass, Field, relations (BelongsTo/HasMany/HasOne/BelongsToMany/Morph*), the async ORM query builder, the mapper, and model lifecycle hooks. Read before editing model.py, metaclass.py, fields.py, query.py, mapper.py, or drivers/."
user-invocable: true
---

# Uvicore ORM Development

The ORM is a Pydantic-v1-backed, async, relation-rich model layer that compiles to the low-level DB
query builder (see `uvicore-database-dev`). Pydantic is **held at v1.10** — do not use v2 APIs.

## Anatomy of a model

```python
@uvicore.model()
class Post(Model['Post'], metaclass=ModelMetaclass):
    __tableclass__ = table.Posts                       # links to the @uvicore.table() class
    id: Optional[int] = Field('id', primary=True, read_only=True, ...)
    slug: str        = Field('unique_slug', max_length=255)   # field name != column name OK
    creator: Optional[User] = Field(None, relation=BelongsTo('uvicore.auth.models.user.User'))
Post.update_forward_refs()                              # required when relations use forward refs
```
Real examples: `tests/apps/app1/models/post.py` (every relation type), `auth/models/user.py`.

Key files:
- `orm/model.py` — `Model` class: `query()`, `insert()`, `insert_with_relations()`, `save()`,
  `create()`/`add()`, `set()`, `delete()`, `link()`/`unlink()`, lifecycle hooks.
- `orm/metaclass.py` — `ModelMetaclass.__new__` does the heavy lifting (below).
- `orm/fields.py` — `Field(...)` + all `Relation` subclasses.
- `orm/query.py` — `OrmQueryBuilder` (async, chainable).
- `orm/mapper.py` — `Mapper` field↔column and dict/row↔model conversion.
- `orm/drivers/` — `sqlalchemy.py` (default backend, currently thin) and `api.py` (remote-API
  backend, future). Contracts: `contracts/model.py`, `field.py`, `relation.py`, `mapper.py`,
  `builder.py`.

## ModelMetaclass (`orm/metaclass.py`) — what it builds

On class creation it:
1. Collects every `Field` instance from the namespace into `__modelfields__: Dict[str, Field]`,
   converting each to a Pydantic `FieldInfo` (whitelisted props only).
2. Merges parent `__modelfields__` so **model subclassing/extension inherits fields**, and inherits
   `__connection__`, `__tablename__`, `__table__`, `__tableclass__`.
3. From `__tableclass__` resolves `connection`, `tablename`, and builds the SQLAlchemy `__table__`.
4. Registers field `callback` functions into `__callbacks__`.

Class-level helpers it exposes: `pk`, `connection`, `tablename`, `table`, `modelfields`,
`modelname`, `modelfqn`, `modelfield(name)`, `selectable_columns(table=None, show_writeonly=False)`,
`info()`, and async `execute()/fetchall()/fetchone()`.

**Reserved field names** (collide with methods/Pydantic): `query, insert, insert_with_relations,
mapper, create, save, delete, link, unlink` (+ Pydantic's `dict, json, parse_obj, ...`).

## Fields (`orm/fields.py`)

`Field(column=None, *, name, primary, title, description, default, sortable, searchable,
read_only, write_only, callback, evaluate, relation, json, properties, min_length, max_length,
example)`.
- `column` is the DB column; `None` for pure relations or computed fields.
- `read_only=True` → excluded from `mapper().table()` writes; `write_only=True` → excluded from
  query selects. Both map to OpenAPI readOnly/writeOnly.
- `callback` = method name computed at `__init__`; `evaluate` = fn applied when mapping a DB row.

## Relations (all subclass `Relation`, `fields.py`)
- `BelongsTo(model, foreign_key='id', local_key='{field}_id')` — FK lives on THIS table.
- `HasOne(model, foreign_key, local_key='id')` / `HasMany(...)` — FK lives on the RELATED table
  (`foreign_key` required).
- `BelongsToMany(model, join_tablename, left_key, right_key)` — pivot table.
- `Morph`/`MorphOne`/`MorphMany(model, polyfix=...)` — polymorphic; derives
  `{polyfix}_type` + `{polyfix}_id`. `MorphToMany(model, join_tablename, polyfix, right_key)`.
- Helpers: `.is_one()`, `.is_many()`, `.is_type(*types)`, `.fill(field)` (resolves keys + loads
  `entity`). `*Many` relations support `dict_key`/`dict_value`/`list_value` to shape output.

When you add/modify a relation type, update: `fill()` defaulting, the join construction in
`OrmQueryBuilder._build_orm_relations()` (`query.py`), result hydration in `_build_orm_results()`,
and the write paths in `model.insert_with_relations()`/`create()`/`link()`/`set()`.

## ORM query builder (`orm/query.py`) — async, chainable

`Model.query()` → `OrmQueryBuilder(entity)`. Filtering/shaping (return `self`):
`where(col, op='=', val)`, `or_where([...])`, `include('creator', 'roles', 'creator.contact')`
(eager-load, dot-nested), `filter(...)`/`or_filter(...)` (filter *Many relations after join),
`sort(col, order)` (within Many relations), `order_by(col, order)` (main query), `limit`, `offset`,
`key_by(field)`, `show_writeonly([...])`, `distinct()`, `cache(key, seconds=, store=)`.
Terminal (await): `get()`, `find(pk)`, `count()`, `delete()`, `update(**kwargs)`. Introspection:
`sql(method='select')`, `queries(method='select')`.

`.where()` filters the main query *before* joins; `.filter()` filters the related rows of a Many
relation. Each `*Many` include becomes a **separate SQL query** (then deduped + merged by PK);
`*One` includes are joined into the main query with the relation name as the table alias (columns
come back prefixed, e.g. `creator__username`).

## Writes & lifecycle (`orm/model.py`)
- `await Model.insert(models)` — bulk; no child relations. `await Model.insert_with_relations([...])`
  — single-row inserts that walk nested relations (BelongsTo child-first; HasOne/Many parent-first;
  Morph sets type+id; *ToMany links via pivot).
- `await instance.save()` — insert-or-update by PK, no relations. `await instance.create(rel, models)`
  (alias `add`) — insert children + link. `set(rel, models)` — replace. `delete(rel=None)`.
  `link/unlink(rel, models)` — pivot rows only.
- Hooks (async, fire events `uvicore.orm-{modelfqn}-BeforeInsert` etc.): `_before_insert`,
  `_after_insert`, `_before_save`, `_after_save`, `_before_delete`, `_after_delete`. Override in a
  model and call `await super()._before_save()`.

## Conventions for ORM changes
- Field name ≠ column name is fine and common; the **Table schema** owns column names.
- Don't break model subclass field inheritance (the `__modelfields__` merge in the metaclass).
- Keep `read_only`/`write_only` honored in `selectable_columns()` and `mapper().table()`.
- Models are non-singleton IoC bindings (`{module}.{Class}`); Table classes are singletons.
- Test relation changes against `tests/test_db/test_orm/` (one file per relation type) and
  the basics in `tests/test_db/test_orm/test_query_basics.py`. See `uvicore-testing`.
