---
name: uvicore-app-scaffolding
description: 'Scaffold or extend a Uvicore app, package, CLI command, API route, web route, provider, config, database feature, or server-rendered view using standard Uvicore structure. Use when creating new Uvicore app features or wiring generated code into provider, bootstrap, config, routes, models, tables, seeders, views, and commands.'
argument-hint: 'Describe the Uvicore app or feature to scaffold'
user-invocable: true
---

# Uvicore App Scaffolding

Use this skill when the task is to scaffold or extend a Uvicore app intentionally, not just to explain the framework.

## When To Use

- Create a new runnable Uvicore app package.
- Add a new CLI command group or command.
- Add a new API or web feature.
- Add a model-backed feature with tables, models, seeders, routes, and views.
- Wire a new feature into a Uvicore provider so it actually loads.

## Outcome

Produce code that follows Uvicore conventions for bootstrap, provider lifecycle, config layout, HTTP structure, database registration, and testing.

## Procedure

1. Identify whether the request is primarily CLI, API, web, database, or shared service work.
2. Confirm the target package and the running app entrypoints before generating files.
3. Follow the standard Uvicore package layout from [app structure](./references/app-structure.md).
4. Add or update config first when the feature needs prefixes, connections, drivers, bindings, or toggles.
5. Update `package/provider.py` so the feature is registered in `boot()` using Uvicore helper methods.
6. Keep `register()` limited to config merges, lightweight bindings, and early listeners.
7. For HTTP work, keep web and API concerns separate and use config-driven prefixes.
8. For database work, add tables, models, and seeders together when the feature needs all three, then register them in the provider.
9. For CLI work, create dedicated command modules and register command paths in the provider.
10. Add or update tests following [testing conventions](./references/testing-conventions.md).
11. Verify that generated code includes the provider and config changes needed to make the feature load.

## Scaffolding Rules

- Do not scaffold Uvicore features as standalone modules that are never registered.
- Do not put heavy work in `register()`.
- Do not hardcode prefixes, connection names, or driver choices when they belong in config.
- Do not mix CLI, API, web, and database responsibilities into one file unless the existing package already does so deliberately.
- Prefer the sample app shape and naming over generic Python project scaffolding.

## Required Deliverables By Feature Type

- New runnable app:
  `package/bootstrap.py`, `package/provider.py`, `config/app.py`, and `http/server.py` if HTTP is enabled.
- New CLI feature:
  command module, provider command registration, config only if needed, tests.
- New API feature:
  route registration, API handler/controller, config updates if needed, tests.
- New web feature:
  web routes, controller or handler, views, public/assets if needed, provider registration, tests.
- New database feature:
  tables, models, seeders, provider registration, tests.

## References

- [app structure](./references/app-structure.md)
- [testing conventions](./references/testing-conventions.md)
