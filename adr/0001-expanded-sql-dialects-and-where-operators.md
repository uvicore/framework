# ADR 0001: Expanded SQL dialect support, driver/port defaults & WHERE operators

- **Status:** Accepted
- **Date / version:** 2026-06-17 (uvicore 0.4.x)

> Backfilled from commit `0717309`.

## Context

The database layer supported only a small set of dialects and a limited set of query-builder
comparison operators. Real-world apps need broader engine support (incl. cloud/distributed engines)
and richer `WHERE` expressiveness, and we wanted confidence via tests against *real* engines, not
just SQLite.

## Decision

- **Dialects**: expand `db.py` `SUPPORTED_DIALECTS` to `postgresql` (+ `postgres` alias normalized to
  `postgresql`), `mysql`, `mariadb`, `sqlite`, `snowflake`, `mssql`, `oracle`, `cockroachdb`.
- **Defaults**: add `SERVER_DIALECT_DEFAULTS` (default async driver + port per server dialect) and
  deterministic **async-vs-sync driver detection** via `SUPPORTED_ASYNC_DRIVERS` (no fragile
  bare-except sync fallback). SQLite/Snowflake get their own URL shapes.
- **WHERE operators**: add `like`, `ilike`, `in`, `not in`, `between`, `null`, `not null`, and the
  comparison operators (`!=`, `<`, `<=`, `>`, `>=`) to the query builder.
- **Testing**: add docker-based cross-DB integration tests for postgres/mysql/mariadb under
  `tests/integration/`.

## Consequences

- **+** Broad, portable database support and far more expressive queries.
- Cross-dialect gotchas to respect (now documented): `LIKE` is case-sensitive on Postgres (use
  `ilike`); never insert an explicit NULL auto-increment PK; row order isn't guaranteed without
  `.order_by()`.
- Integration tests require docker; run via `bin/test-db-integration.sh {postgres|mysql|mariadb|all}`.
