# ADR 0009: Configurable engine pooling + Snowflake session resilience

- **Status:** Accepted
- **Date / version:** 2026-08-27 (uvicore 0.4.11)

## Context

`Db.init()` created every SQLAlchemy engine with a **hardcoded** `pool_pre_ping=True` on the sync
branch and **no pool arguments at all** on the async branch. An app could configure the driver
(`options` → `connect_args`) but had no way to influence the pool. That is the wrong place to draw
the line: pooling is the part of the database layer whose right answer is entirely
deployment-shaped — a days-long consumer wants pre-ping and recycling, a request/response API wants
a pool sized to its worker count, and a warehouse with a per-warehouse concurrency ceiling wants
that ceiling respected. The framework cannot guess any of it. The asymmetry was also a silent hole:
async apps (the majority) had no stale-connection protection whatsoever.

Separately, **Snowflake connections did not survive four hours.** A Snowflake session holds a
session token (~1h) and a MASTER token (~4h). The connector renews the first (`390112` →
`_renew_session()`) but on `390114` MASTER_TOKEN_EXPIRED it only sets `connection.expired = True`,
which nothing in the connector ever reads; key-pair auth has no re-auth path either. So every
long-running process began failing every query with:

```
390114 (08001): Authentication token has expired.  The user must authenticate again.
```

And it never recovered. `snowflake-sqlalchemy` declares no `is_disconnect()`, so SQLAlchemy
classified the expired token as an ordinary `ProgrammingError`: the dead connection was rolled back,
**returned to the pool, and handed straight back out**, forever. An application retry loop could
never win — only a process restart cleared it. `pool_pre_ping` could not rescue it either: its
`SELECT 1` raises that same ordinary error, and `sqlalchemy/pool/base.py` invalidates only on a
`DisconnectionError`. Observed in production on a fleet of infinite-loop stream consumers.

## Decision

**1. A per-connection `pool` config block.** Unprefixed keys (`pre_ping`, `recycle`, `size`,
`max_overflow`, `timeout`, `use_lifo`, `reset_on_return`) map onto `create_engine()`'s `pool_*`
kwargs through `Db.POOL_OPTIONS`, resolved by the pure, unit-testable `Db.engine_pool_kwargs()`.
Unknown keys **raise** at bootstrap rather than being ignored, because a silently-dropped
`pool_recycle` (the prefixed spelling — the obvious mistake) would look configured and do nothing.
Only `pre_ping` is defaulted, to `True`: `size`/`max_overflow` are rejected outright by
SQLAlchemy's `StaticPool`/`NullPool`, which is what a sqlite `':memory:'` url gets, so defaulting
them would break the simplest connection there is. The block is applied **identically** to sync and
async engines.

**2. Snowflake keeps its session alive by default.** `configure_connection()` `.defaults()` the
snowflake connect options to `client_session_keep_alive: True` and
`client_session_keep_alive_heartbeat_frequency: 900`. A framework whose database connection expires
after four hours is not a working database connection, so this is a default rather than something
each app rediscovers the hard way. 900s (not the connector's 3600s) because the connector clamps to
`[master_validity/16, master_validity/4]` = `[900, 3600]` anyway, and a heartbeat is a token-only
REST call — no query, **no warehouse credits** — so the cheap end buys four renewal chances per
master-token window instead of one. `.defaults()` means an app that sets either key always wins.

**3. Terminal Snowflake token codes are DISCONNECTS.** New `uvicore/database/snowflake.py`
registers SQLAlchemy's `handle_error` hook and flips `ctx.is_disconnect = True` for `390110`,
`390113`, `390114`, `390115`, which makes SQLAlchemy invalidate the connection *and* the pool.
`390112` is deliberately excluded — the connector renews it itself, and treating it as a disconnect
would discard a pool that was about to heal.

Two sub-decisions inside (3):

- **`handle_error`, not a dialect subclass.** Teaching `is_disconnect()` to the dialect would mean
  subclassing `SnowflakeDialect` and re-registering it under the `snowflake://` entrypoint —
  hijacking a name the driver owns and silently shadowing whatever a future snowflake-sqlalchemy
  ships. `handle_error` is SQLAlchemy's documented extension point for exactly this.
- **Per engine, not on the `Engine` class.** A class-level listener fires for every dialect in the
  process. `Db.init()` arms each snowflake engine as it builds it, so a Postgres sibling pays
  nothing and an engine rebuilt by a re-init (the runtime warehouse-switch trick) is re-armed.

## Consequences

- **Async connections gain pre-ping.** This is the one user-observable behavior change: one extra
  round-trip per pool checkout, in exchange for never handing application code a connection the
  server closed while it sat idle. Opt out with `'pool': {'pre_ping': False}`. Validated against
  real Postgres, MySQL and MariaDB (cross-dialect suite, 106 tests each).
- **Not breaking.** Sync `pre_ping` keeps its old value, the `pool` block is optional, and both
  Snowflake defaults are overridable per connection. No upgrade-guide action required.
- **Snowflake becomes viable for long-lived processes** without every app reimplementing the fix.
  The statement that hits a dead token still raises — callers must still retry. That is deliberate:
  the framework restores the *connection*, and only the caller knows whether its unit of work is
  safe to replay.
- **`snowflake-sqlalchemy` remains app-supplied**, not a framework dependency, so the framework test
  suite cannot build a real Snowflake engine. `tests/test_db/test_pooling.py` therefore stands in a
  sqlite engine for the driver in the one wiring test that needs one; everything else under test is
  uvicore's own code.
- **Watch:** if snowflake-sqlalchemy ever ships its own `is_disconnect()`, our listener becomes
  redundant but stays harmless (it returns early when `ctx.is_disconnect` is already set).
