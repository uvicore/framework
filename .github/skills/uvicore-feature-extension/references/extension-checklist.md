# Uvicore Extension Checklist

Use this checklist before finishing an existing-feature change.

## Wiring

- Provider updated if new runtime behavior was added.
- `register()` still only contains config merges, lightweight bindings, and early listeners.
- `boot()` owns routes, commands, views, public/assets, db, redis, and other real registration work.

## Config

- New toggles, prefixes, drivers, or connection names live in config.
- `config/app.py` still aggregates the app-level config clearly.
- Concern-specific config files remain split by feature area.

## HTTP

- Web and API changes stay separated.
- Routes are registered through provider helpers.
- New handlers/controllers fit the existing package path and naming.

## Database

- Tables, models, and seeders stay in their dedicated folders.
- Provider registration is updated when database-backed behavior changes.

## CLI

- Commands remain in dedicated modules.
- Provider command registration is updated.

## Tests And Docs

- Tests cover the changed runtime behavior and wiring.
- Docs are updated when public behavior or developer workflow changed.
