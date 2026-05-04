# Uvicore Review Checklist

## Code And Wiring

- `register()` only contains config merges, lightweight bindings, or early listeners.
- `boot()` contains actual registration work.
- Provider wiring was updated when runtime behavior changed.
- Config files were updated when prefixes, connections, drivers, bindings, or defaults changed.
- HTTP changes keep web and API concerns separate.
- CLI changes are registered through provider command registration.
- Database-backed changes update models, tables, seeders, and provider registration consistently.

## Tests

- Tests cover changed behavior, not just imports.
- Tests cover provider/config/runtime integration when relevant.
- Regression tests exist for fixed bugs.

## Docs

- Relevant docs pages were updated in the docs workspace.
- New docs pages are wired into `mkdocs.yml` if they are meant to be published.
- Stale or superseded pages were cleaned up if new docs replaced them.

## Release Notes

- Breaking, deprecated, renamed, or notable changes update epologue docs.
- Changelog filename matches the target release version.
- Upgrade filename matches the source and destination versions.
