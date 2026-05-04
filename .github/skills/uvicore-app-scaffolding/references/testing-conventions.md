# Uvicore Testing Conventions

## General Rules

- Follow the style already used in `framework/tests/`.
- Prefer focused tests per concern rather than one large integration test file.
- Use `@pytest.mark.asyncio` for async behavior.
- Reuse existing fixtures and app bootstrap patterns instead of inventing new setup flows.

## What To Test

- Provider and config wiring for newly added features.
- CLI commands for registration and expected behavior.
- API and web route behavior for new HTTP features.
- Database tables, models, relationships, and seeders when data features are introduced.
- Service integration points such as cache, events, auth, db, redis, or mail when the feature depends on them.

## Test Placement

- Framework-level behavior should be tested under `framework/tests/` in the closest matching feature folder.
- App-level behavior should be tested under the app's `tests/` folder.
- Keep directory naming aligned with the feature area such as `test_http`, `test_console`, `test_db`, or `test_unit`.

## Expectations

- Generated features should include tests unless the user explicitly asks not to add them.
- Tests should validate that new code is actually registered and reachable through the Uvicore lifecycle.
- Prefer testing real framework behavior over shallow import-only checks when practical.
