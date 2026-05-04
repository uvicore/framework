---
name: uvicore-feature-extension
description: 'Extend or modify an existing Uvicore feature without scaffolding a brand new app structure. Use when updating existing providers, config, routes, commands, models, views, docs wiring, or tests so a change fits the current Uvicore package cleanly.'
argument-hint: 'Describe the existing Uvicore feature to extend'
user-invocable: true
---

# Uvicore Feature Extension

Use this skill when the target already exists and the job is to extend, refine, or wire additional behavior into the current Uvicore package structure.

## When To Use

- Add behavior to an existing provider, route group, controller, command, model, table, seeder, or view.
- Extend an existing CLI, API, or web feature.
- Add config-driven options to an existing feature.
- Update provider wiring, registration order, or feature flags for code that already exists.
- Add tests and documentation for an existing feature change.

## Do Not Use

- Do not use this skill to scaffold a brand new runnable app from scratch.
- Do not use this skill when the main task is creating a fresh package layout.
- Use the scaffolding skill instead when the request is primarily generation of a new Uvicore package surface.

## Outcome

Apply incremental changes that preserve the existing Uvicore package layout, provider lifecycle, config structure, tests, and docs.

## Procedure

1. Inspect the existing feature entrypoints first: provider, config, routes, commands, models, tables, seeders, views, tests, and docs.
2. Extend the current feature in place rather than introducing a parallel structure.
3. If the change adds runtime behavior, update the provider `boot()` wiring so the behavior actually loads.
4. If the change adds a toggle, prefix, driver, connection, binding, or package setting, update config before changing runtime code.
5. Preserve the current split between CLI, API, web, database, and shared services.
6. Add focused tests near the changed behavior using Uvicore testing patterns.
7. Update documentation in the docs workspace when the change affects public behavior, app structure, CLI usage, routing, config, or framework expectations.

## Extension Rules

- Prefer modifying the existing provider helper methods such as `register_views()`, `register_routes()`, and `register_commands()` when they already exist.
- Do not move code into `register()` unless it is config merge or very early binding work.
- Keep config changes localized to the correct concern-specific config files.
- Reuse the current route organization and controller loading style already used by the feature.
- Reuse the current model, table, and seeder registration flow instead of adding import side effects.

## Required Checks

- Is the feature wired in the provider?
- Is config updated if behavior depends on config?
- Are tests updated for the changed behavior?
- Do docs need updating in `docs/docs/` and possibly `mkdocs.yml` navigation?

## References

- [extension checklist](./references/extension-checklist.md)
- [docs mapping](./references/docs-mapping.md)
