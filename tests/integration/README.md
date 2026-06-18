# Uvicore Database Integration Test Matrix

The default unit suite (`poetry run ./bin/test.sh`) runs against in-memory **SQLite**.
This directory runs the **same** schema, seeders and ORM/query tests end-to-end against
**real** database engines in throwaway docker containers, so dialect-specific gaps are
caught (SQLite is very forgiving; Postgres/MySQL are strict).

## Run it

```bash
poetry run ./bin/test-integration.sh postgres     # one engine
poetry run ./bin/test-integration.sh mysql
poetry run ./bin/test-integration.sh mariadb
poetry run ./bin/test-integration.sh all          # every engine, sequentially
KEEP_UP=1 poetry run ./bin/test-integration.sh postgres   # leave the container running
```

The runner brings the container up, waits for its healthcheck, runs the suite with the
matching `env/<backend>.env` file, then tears the container down.

## How it works

- `docker-compose.yml` defines Postgres / MySQL / MariaDB on offset ports (55432 / 53306 / 53307).
- `env/<backend>.env` points **both** the `app1` and `auth` connections at the same server,
  so they share one metakey/metadata space exactly like the SQLite `:memory:` default.
- The connection configs (`tests/apps/app1/config/database.py` and
  `uvicore/auth/config/package.py`) are env-driven: set `DB_APP1_DIALECT` / `DB_AUTH_DIALECT`
  (plus host/port/user/password) and the framework builds the right SQLAlchemy URL.
- Only the dialect-agnostic suites run (portable assertions: sorted/set comparisons,
  `ilike` for case-insensitive matching, database-generated primary keys). The broader
  `tests/test_db/test_orm` unit suite intentionally assumes SQLite behavior (implicit row
  order, case-insensitive `LIKE`) and is not part of the cross-db run.

## Cross-dialect gotchas this matrix enforces

- **Primary keys**: never send an explicit `NULL` for an auto-increment PK. SQLite tolerates
  it; Postgres/MySQL reject it. The ORM omits a `None` PK from inserts (see
  `test_insert_autopk.py`).
- **By-id lookups**: `find(id)` coerces the value to the pk column's Python type, so a string
  id (e.g. from a URL path) does not blow up on Postgres with `integer = varchar`.
- **`LIKE` is case-sensitive on Postgres** (and per the SQL standard) but case-insensitive on
  SQLite/MySQL's default collation. Use **`ilike`** for portable case-insensitive matching.
- **Row order is not guaranteed** without an explicit `.order_by()` on Postgres/MySQL.

## Adding a backend

Add a service to `docker-compose.yml` (with a healthcheck) and an `env/<name>.env` file,
then add the name to the `case` in `bin/test-integration.sh`. Any standard SQLAlchemy
server dialect works as long as its driver is in the `database` extra.
