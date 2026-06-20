# Uvicore Integration Test Matrix

The default unit suite (`poetry run ./bin/test.sh`) runs against in-memory backends
(SQLite for the database, the `array` in-memory store for the cache). This directory
runs the **same** behavior end-to-end against **real** services in throwaway docker
containers, so gaps the in-memory backends hide are caught:

- **Database** (`test_cross_db.py`) — real Postgres / MySQL / MariaDB engines.
- **Redis cache** (`test_redis_cache.py`) — a real redis server behind the `redis` cache backend.
- **Redis service** (`test_redis_service.py`) — the generic `uvicore.redis` connection helper + passthrough against a real redis server.

---

# Database Integration Test Matrix

The default unit suite (`poetry run ./bin/test.sh`) runs against in-memory **SQLite**.
This directory runs the **same** schema, seeders and ORM/query tests end-to-end against
**real** database engines in throwaway docker containers, so dialect-specific gaps are
caught (SQLite is very forgiving; Postgres/MySQL are strict).

## Run it

```bash
poetry run ./bin/test-db-integration.sh postgres     # one engine
poetry run ./bin/test-db-integration.sh mysql
poetry run ./bin/test-db-integration.sh mariadb
poetry run ./bin/test-db-integration.sh all          # every engine, sequentially
KEEP_UP=1 poetry run ./bin/test-db-integration.sh postgres   # leave the container running
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
then add the name to the `case` in `bin/test-db-integration.sh`. Any standard SQLAlchemy
server dialect works as long as its driver is in the `database` extra.

---

# Redis Cache Integration Tests

The default unit suite exercises the in-memory **`array`** cache backend (`CACHE_STORE`
defaults to `array` in `tests/apps/app1/config/cache.py`). `test_redis_cache.py` exercises
the **`redis`** cache backend end-to-end against a real redis server, covering the full
`Cache` contract: `put`/`get`/`has`, multi-key get/put, `forget`, `pull`, `add`, `remember`,
`increment`/`decrement`, real server-enforced TTL expiry, `touch`, pickle round-tripping of
arbitrary python objects, key prefixing, and prefix-scoped `flush`.

## Run it

```bash
poetry run ./bin/test-cache-integration.sh
KEEP_UP=1 poetry run ./bin/test-cache-integration.sh   # leave the redis container running
poetry run ./bin/test-cache-integration.sh tests/integration/test_redis_cache.py -x   # extra pytest args
```

The runner brings up a `redis:7-alpine` container (offset port **56379**), waits for its
healthcheck, then runs the suite with `env/redis.env` (which sets `CACHE_STORE=redis` and
points the `cache` redis connection at the container).

## How it works

- The tests resolve the redis store explicitly via `uvicore.cache.store('redis')`, so they
  verify the redis backend regardless of which store is the configured default.
- The `cache` fixture **skips** the whole module if no redis server is reachable, so the
  suite is harmless under the plain `./bin/test.sh` run (it skips when no redis is up, and
  runs for real when one is — e.g. a local redis on `127.0.0.1:6379` or the docker container).
- The fixture is `loop_scope="session"` so it shares the same event loop as the tests and
  the session-scoped `app1` fixture. Without this, pytest-asyncio runs a function-scoped
  async fixture in its own loop, the redis connection pool binds to that loop, and every test
  fails with *"Future attached to a different loop"* when it reuses the cached pool.

## Gotcha this suite caught

`redis` `DEL` requires at least one key — `Cache.flush()` on an **empty** cache was calling
`redis.delete()` with no arguments and raising. Fixed in `uvicore/cache/backends/redis.py`
(skip the delete when no prefixed keys exist). The `array` backend never had this problem,
so the in-memory unit suite never exposed it.

---

# Redis Service Integration Tests

`uvicore/redis` (the `Redis` service, reached via `from uvicore.redis import Redis`) is a thin
connection helper + passthrough — separate from caching. It resolves named connections from
config, builds their URLs, lazily opens and **caches one `redis.asyncio` pool per connection
URL**, and hands back the raw async redis client. The default unit suite only asserts the
service is wired up; `test_redis_service.py` exercises it end-to-end against a real redis server.

It covers:

- **Connection management** — default selection (`app1`), named lookup, `redis://host:port/db`
  URL building, unknown-connection errors, one cached engine per URL, and **database-level
  isolation** between the `app1` (db 0) and `cache` (db 2) connections.
- **The passthrough** — a representative slice of real redis commands through the returned
  client: strings (`set`/`get`/`setnx`/`append`), counters (`incr`/`decrby`), expiry
  (`expire`/`ttl`/`persist`/`setex`), hashes, lists, sets, and `keys` pattern scans.

## Run it

```bash
poetry run ./bin/test-redis-integration.sh
KEEP_UP=1 poetry run ./bin/test-redis-integration.sh
poetry run ./bin/test-redis-integration.sh tests/integration/test_redis_service.py -x
```

Like the cache runner, it uses the `redis:7-alpine` container (port **56379**) and `env/redis.env`.
All test keys are namespaced under `uvicore-redis-itest:` and cleaned up per test, so the suite is
safe to run against a shared/local redis, and it **skips** entirely when no redis is reachable.
The fixture is `loop_scope="session"` for the same event-loop reason described in the cache section.
