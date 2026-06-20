---
name: uvicore-database-dev
description: "Working on the Uvicore database layer, configuration system, and the foundational Dict/SuperDict type — uvicore/database/ (db service, low-level query builder, Table, seeders, connections), uvicore/configuration/ (config + env()), uvicore/typing/dictionary.py. Read before editing db.py, builder.py, query.py, table.py, the config service, or the Dict type."
user-invocable: true
---

# Uvicore Database, Config & SuperDict Development

Three tightly-related foundations: the `db` service (multi-connection async SQLAlchemy core), the
config system (deep-merged SuperDicts), and the `Dict`/SuperDict type used everywhere.

## Dict / SuperDict (`uvicore/typing/dictionary.py`) — used by config, connections, routes, packages

`Dict(_SuperDict, dict)` and `OrderedDict(_SuperDict, _OrderedDict)`. `deep_merge()` lives in
`support/dictionary.py`. Core methods:
- `.dotget('a.b.c')` / `.dotset('a.b.c', val)` — dot-path access. Bracket `[a.b]` escapes dots.
- `.merge(*dicts)` (alias `.update`) — **deep merge, override wins**. `.defaults(*dicts)` — deep
  merge, **only fills missing** keys. `.clone()`/`.deepcopy()`. `.freeze()`/`.unfreeze()`.
  `.to_dict()`/`.dict()`.
- Missing keys **auto-vivify** to nested `Dict` (unless frozen) — `cfg.a.b.c = 1` just works.
- Attribute access (`cfg.database.default`) and subscript both work; `|` merges.

Prefer these over plain dict/`collections.OrderedDict` to match the codebase.

## The `db` service (`uvicore/database/db.py`, alias `uvicore.db`)

Singleton (`@uvicore.service(..., singleton=True)`). `init(default, connections)` is called on the
`Booted` event by `database/package/bootstrap.py` after gathering connections from every package.

- **Metakey concept**: connections sharing the same server+database collapse to one `metakey`
  (`dialect@host:port/database`, or `dialect://db` for sqlite) so they share one SQLAlchemy
  `MetaData`/engine — this is what makes cross-connection foreign keys work.
- Lookup: `connection(name=None)`, `metakey(name)`, `metadata(name)`, `engine(name)`,
  `table('users','auth')` / `table('auth.users')`, `tablename(...)` (applies prefix),
  `packages(metakey=)`.
- Query: `query(connection)` → `DbQueryBuilder`. Raw async: `execute`, `all`, `first`, `scalar`,
  `insertone`, `insertmany`.
- Backends: `sqlalchemy`. Dialects: postgresql/mysql/sqlite/snowflake with async drivers
  (asyncpg/aiomysql/aiosqlite/...). Dialect defaults (host/port/driver/prefix) are filled in
  `init()`.

## Connection contract (`uvicore/contracts/connection.py`)
`Connection(Dict)` — dynamic SuperDict with `name, backend, driver, dialect, host, port, database,
username, password, prefix, metakey, url, is_async`. Defined in `config/package.py` under
`database.connections.<name>`, usually via `env(...)`.

## Low-level query builder (`database/builder.py` + `database/query.py`)
`DbQueryBuilder` (from `uvicore.db.query('conn')`) is the SQLAlchemy-Core layer the **ORM compiles
down to**. Chainable: `table()`, `select()`, `where(col, op, val | [(...)] | sa_expr)`,
`or_where()`, `join()/outer_join()`, `order_by()`, `group_by()`, `limit()`, `offset()`,
`distinct()`, `cache(key, seconds=, store=)`. Terminal async: `get/all/first/one/one_or_none/count/
scalar/scalar_one/scalars/find(pk|col=val)/update(**kw)/delete()`; `sql('select')` for raw SQL.
Operators: `= == != > < >= <= in !in like !like`. Internal dataclasses: `Query`, `Column`, `Join`
(`builder.py`). The ORM builder (`orm/query.py`) builds on the same `Query` shape — keep them
aligned when changing builder internals.

## Tables (`database/table.py`)
```python
@uvicore.table()
class Users(Table):
    name = 'users'           # no prefix here — connection prefix is applied in __init__
    connection = 'auth'
    schema = [sa.Column('id', sa.Integer, primary_key=True), ...]
    schema_kwargs = {}
```
`@uvicore.table()` binds as a **singleton**. `__init__` pulls `metadata(connection)`, prepends the
connection prefix to `name`, builds the `sa.Table` (only if backend is sqlalchemy). Example:
`auth/database/tables/users.py`.

## Seeders
`@uvicore.seeder()` async fn that uses ORM models. Registered via
`self.register_db_seeders(['pkg.database.seeders.seed'])`. Run by the `db` CLI commands
(`database/commands/db.py`): `db create|drop|recreate|seed|reseed|connections <conns>` (tables
created/dropped in topological FK order; conns comma-separated). The test conftest calls
`db.drop_tables/create_tables/seed_tables('app1')` directly.

## Config system (`uvicore/configuration/`)
- `Configuration` is a `Dict` subclass bound singleton with aliases `Config/config`; reachable as
  `uvicore.config`.
- `env` (`configuration/__init__.py`) is an `environs.Env` instance: `env('KEY', default)`,
  `env.int(...)`, `env.bool(...)`. Use in `config/package.py` for all environment-driven values.
- Merging: provider `register()` calls `self.configs([...])`, each value deep-merged via
  `uvicore.config.dotset(key, value)` → later packages override earlier; an app overrides framework
  config by re-declaring the same key. A package's final merged config is `self.package.config`
  (i.e. `uvicore.config.dotget(package.name)`).
- `registers` gate dict (in `config/package.py`) toggles what providers load
  (`models/tables/seeders/web_routes/api_routes/views/assets/commands`).

## Where operators (`builder.py` `_where_expression`)
Single source of truth for `where`/`or_where`/`filter`/`or_filter` on BOTH builders.
Supported (case- + whitespace-insensitive): `= == != <> > < >= <=`, `in`, `!in`/`not in`,
`like`, `!like`/`not like`, **`ilike`/`!ilike`** (case-insensitive, portable), `between`/
`not between`, `is`/`is null`, `is not`/`is not null`. Unknown operator or column → clear
raised error (not a silent wrong result). Add new operators here, not in callers.

## Dialect / connection layer (`db.py` `configure_connection`)
- `configure_connection()` is pure (no engine creation) → unit-testable per dialect
  (`tests/test_db/test_dialects.py`). `init()` calls it then creates the engine.
- `postgres` is normalized to `postgresql` (SQLAlchemy dropped the alias). Any standard server
  dialect works via `SERVER_DIALECT_DEFAULTS` (postgresql/mysql/mariadb/mssql/oracle/cockroachdb).
- Async vs sync is **deterministic** via `SUPPORTED_ASYNC_DRIVERS` (no bare-except fallback).
- `connection.url` stores the real password (str(URL) masks it; a masked url can't make an engine).

## Cross-dialect correctness (SQLite is forgiving; Postgres/MySQL are strict)
- **Never insert an explicit NULL auto-increment PK** — `mapper.table()` omits a `None` primary
  key so the DB generates it (SQLite tolerated the NULL; Postgres/MySQL reject it).
- **`find(pk)` coerces** the value to the pk column's Python type (string id from a URL path
  would otherwise fail on Postgres with `integer = varchar`).
- **`LIKE` is case-sensitive on Postgres**; use `ilike` for portable case-insensitive matching.
- **Row order isn't guaranteed** without `.order_by()` on Postgres/MySQL.

## Conventions for db/config changes
- Don't break the metakey/shared-metadata design — it's why FKs span connections.
- Keep the low-level builder and the ORM builder's `Query` shape consistent.
- Table `name` must NOT include the prefix; the prefix is config-driven and applied at runtime.
- New dialect support: add it to `SUPPORTED_DIALECTS` + `SERVER_DIALECT_DEFAULTS` (and any async
  driver to `SUPPORTED_ASYNC_DRIVERS`). Validate with `test_dialects.py`.
- Use `env()` for anything environment-specific; never hardcode.
- Test against `tests/test_db/`, and run the **cross-db matrix** (`./bin/test-db-integration.sh all`,
  see `tests/integration/`) when touching `database/` or `orm/`. See `uvicore-testing`.
