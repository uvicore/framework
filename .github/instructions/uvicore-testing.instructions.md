---
description: "Use when adding or modifying Uvicore tests, or when generating new Uvicore features that should include framework-style tests. Covers pytest structure, async patterns, fixture usage, test placement, and expectations for provider/config wiring tests."
name: "Uvicore Testing Conventions"
---
# Uvicore Testing Conventions

Use these rules when generating tests for Uvicore framework code or for Uvicore app features.

## General Style

- Follow the patterns already established in `framework/tests/`.
- Prefer focused tests by feature area instead of one large mixed integration file.
- Use `@pytest.mark.asyncio` for async behavior.
- Reuse the existing test app and fixtures when testing framework behavior instead of inventing a new bootstrap flow.
- Keep test names explicit about the behavior being validated.

## Placement

- Put framework tests under the closest matching `framework/tests/` feature folder.
- Use existing groupings such as `test_db`, `test_events`, `test_ioc`, `test_http`, `test_console`, `test_unit`, and similar feature folders.
- Do not add new tests under `framework/tests/apps/` unless the task is explicitly about the stub app itself.

## What New Features Must Test

- Provider wiring so new features are actually registered.
- Config-driven behavior when prefixes, connections, drivers, or bindings are added.
- CLI command registration and execution behavior for new commands.
- API or web routing behavior for new HTTP features.
- Database tables, models, relationships, callbacks, and seeders for new data features.
- Integration with cache, events, auth, redis, mail, or db when the feature depends on them.

## Preferred Test Shape

- Prefer testing real framework behavior over shallow import-only assertions when practical.
- Assert user-visible outcomes such as route responses, registered commands, query results, or config effects.
- Keep setup minimal and rely on shared fixtures when possible.
- Add regression tests for bugs that were fixed.

## Expectations For Generated Code

- New Uvicore features should include tests unless the user explicitly says not to add them.
- If a feature adds provider changes, config changes, and runtime behavior, tests should cover all three layers where reasonable.
- If a feature cannot be tested end to end, add the highest-value focused tests closest to the changed behavior.
