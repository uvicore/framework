---
name: uvicore-testing
description: "Writing and running tests for the Uvicore framework itself. Covers the bin/test*.sh scripts, the app1 reference-app fixture + in-memory SQLite bootstrap in tests/conftest.py, async pytest patterns, and where tests for each subsystem live. Use whenever adding/changing framework behavior that needs test coverage, or when running the suite."
user-invocable: true
---

# Uvicore Framework Testing

Framework tests live in `tests/` and run against the **`app1` reference app**
(`tests/apps/app1/`) booted against an **in-memory SQLite** database. Reuse the existing fixtures
and app — do not invent a new bootstrap flow.

## Running

This repo uses **Poetry** — run everything through `poetry run`, from the `framework/` directory.

- All tests: `poetry run ./bin/test.sh` — sets `PYTHONPATH=./tests/apps`, runs pytest with color,
  ignores `tests/test_database`, passes extra args through. (~361 tests, a few seconds.)
- A subset: `poetry run ./bin/test.sh tests/test_orm` or
  `poetry run ./bin/test.sh tests/test_db/test_orm/test_find.py`.
- Coverage: `poetry run ./bin/test-cov.sh` (term-missing over `uvicore` + `tests/apps/app1`), HTML
  via `poetry run ./bin/test-cov-html.sh`.
- Markers config: pytest-asyncio. Pydantic is v1.10; Python ≥3.10.
- Format check: `poetry run ./bin/black-check.sh`.

## How the harness boots (`tests/conftest.py`)

- `event_loop` — session-scoped loop.
- `app1` (session, async) — the workhorse fixture. It:
  1. `from app1.package import bootstrap; bootstrap.Application(is_console=False)()` (boots the full
     Uvicore app — providers register + boot).
  2. dispatches `console.events.command.PytestStartup` (the DB layer listens → connects all DBs).
  3. `db.drop_tables/create_tables/seed_tables('app1')` to build + seed the in-memory schema.
  4. yields; on teardown dispatches `PytestShutdown` (disconnect).
- `client` (session, async) — `httpx.AsyncClient(app=uvicore.app.http, base_url='http://testserver')`
  for HTTP tests.

**Every test that touches the app takes the `app1` fixture** (and `client` for HTTP). Imports of
models/services go *inside* the test fn (after the app is booted), e.g.:
```python
@pytest.mark.asyncio
async def test_orm_query_first(app1):
    from uvicore.auth.models.user import User
    users = await User.query().limit(1).get()
    assert len(users) > 0
```

## Where tests go (mirror the subsystem)

`tests/` folders: `test_auth, test_cache, test_configuration, test_console, test_contracts,
test_db/{test_builder,test_orm,test_raw,test_sa,test_hybrid}, test_exceptions, test_foundation,
test_http, test_http_client, test_ioc, test_jobs, test_logging, test_mail, test_orm, test_package,
test_redis, test_templating, test_typing, test_unit/test_support`. Plus top-level files
`test_uvicore.py, test_events.py, test_integration.py, test_orm_queries.py, test_http_routing.py,
test_container_ioc.py`.

Put new framework tests in the closest matching folder. **Do not** add tests under `tests/apps/`
unless the change is about the stub app itself.

## What to cover when changing the framework
- **Provider wiring**: that a new feature is actually registered/booted and reachable (not just
  importable).
- **Config-driven behavior**: prefixes, connections, drivers, `registers` toggles.
- **ORM**: per relation type (`tests/test_db/test_orm/` has one file per relation), query building,
  callbacks, lifecycle hooks; assert real query results, not just types.
- **HTTP**: route registration + responses via the `client` fixture; Guard/scope enforcement.
- **CLI**: command registration and execution.
- **Contracts**: if you changed a public surface, update `tests/test_contracts/`.
- Add a regression test for every bug you fix.

## Conventions
- `@pytest.mark.asyncio` for async tests; depend on shared fixtures, keep setup minimal.
- Name tests for the behavior, not the function under test.
- Prefer asserting user-visible outcomes (query rows, HTTP responses, registered commands) over
  shallow import-only checks.
- The app1 app exercises every relation type, auto-API, overrides, etc. — read it before writing a
  new test to see the established pattern.
