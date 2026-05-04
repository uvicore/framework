---
description: "Use when building or modifying a Uvicore app, package provider, bootstrap flow, config, CLI commands, HTTP routes, views, database registration, or documentation about Uvicore conventions. Covers register vs boot responsibilities, package structure, and Uvicore best practices."
name: "Uvicore App Conventions"
---
# Uvicore App Conventions

Use these rules when creating or editing a Uvicore app, package, provider, config, CLI command, HTTP route, view, database model/table registration, or related docs.

## Core Model

- Treat Uvicore as a modular full stack async framework for CLI, API, and server-rendered web apps.
- Prefer the package/provider pattern over ad hoc setup code.
- Keep app-specific behavior in the app package and framework behavior in reusable Uvicore packages.
- Preserve Uvicore's separation between bootstrap, provider registration, and provider boot logic.

## Project Structure

- A runnable Uvicore app should have a bootstrap entrypoint in `package/bootstrap.py`.
- Bootstrap should determine the base path, load `.env`, import app config, and call `uvicore.bootstrap(app_config, base_path, is_console)`.
- The running app config belongs in `config/app.py` and should define `name`, `debug`, and `main.package` plus `main.provider`.
- Split config by concern into files such as `config/http.py`, `config/database.py`, `config/cache.py`, `config/auth.py`, `config/logger.py`, and import them into `config/app.py`.
- Package-specific reusable config belongs in package config modules and should be merged through the provider.
- Prefer this package layout for a runnable app package:

```text
<package>/
	commands/
	config/
	database/
		seeders/
		tables/
	http/
		api/
		controllers/
		public/
		routes/
		views/
		server.py
	models/
	package/
		bootstrap.py
		provider.py
```
- Keep bootstrap, provider, config, commands, HTTP, models, database tables, and seeders in those standard folders unless the existing app already uses a deliberate alternative.

## Provider Rules

- Package providers belong in `package/provider.py` and should use `@uvicore.provider()`.
- In `register()`, only define config merges, lightweight bindings, and very early listeners.
- Do not perform real work in `register()`.
- In `boot()`, register routes, commands, views, assets, public paths, database connections, models, tables, seeders, redis connections, and other integration work.
- If work must happen after all packages are booted, prefer the event system instead of forcing execution order manually.
- When generating a provider for a full app, prefer explicit helper methods such as `register_views()`, `register_routes()`, and `register_commands()` called from `boot()`.
- In `boot()`, prefer this order when applicable: registers control, redis connections, database connections, models, tables, seeders, views, routes, commands.
- Use provider mixins that match the feature set being registered, such as CLI, HTTP, Redis, and Db mixins.

## Config Conventions

- Prefer deep-merge-friendly config structures.
- Register package config with `self.configs()` instead of hardcoding values in random modules.
- Put running app concerns in app config and reusable package concerns in package config.
- Prefer environment-driven values through `uvicore.configuration.env` or `Env()` instead of hardcoded environment-specific values.
- Keep prefixes, connection names, mail, cache, logger, and auth settings in config, not in provider methods.
- `config/app.py` should aggregate the other app config modules and remain easy to scan.
- The app `main.package` should point to the package name and `main.provider` should point to the provider class used to run the app.
- Prefer separate `config/package.py` data for reusable package behavior when the package may be included by another running app.

## CLI Conventions

- Build CLI commands with Async Click decorators and register them through the provider.
- Group commands clearly with `self.register_cli_commands(group=..., help=..., commands={...})`.
- Keep command functions in dedicated modules such as `commands/welcome.py`.
- Prefer async-friendly command implementations when interacting with Uvicore services.
- Use module-path registration strings rather than importing command functions inline in the provider.
- Default to one small command module per command concern instead of large multi-command files.
- Prefer stable group names that reflect the package or feature area.

## HTTP Conventions

- Treat web and API routes as separate concerns with separate registration calls.
- Register web routes with `register_http_web_routes()` and API routes with `register_http_api_routes()`.
- Drive URI prefixes from config, not hardcoded literals scattered across route files.
- Keep HTTP entrypoints thin. The server module should bootstrap the app and expose `http = app.http`.
- Prefer Uvicore routing classes and provider registration helpers over custom manual wiring.
- Preserve the distinction between API behavior, server-rendered web behavior, static public files, and assets.
- Place web route definitions under `http/routes/web.py` and API route definitions under `http/routes/api.py` or equivalent package modules that keep the split obvious.
- Put FastAPI-style API handlers under `http/api/` and web controllers under `http/controllers/` when the app uses those layers.
- Keep OpenAPI-serving behavior, docs routes, and web pages aligned with the configured API and web prefixes.

## Views And Assets

- Register template directories with `register_http_views()`.
- Register public paths with `register_http_public()`.
- Register asset paths with `register_http_assets()`.
- Use view composers or template context processors for shared template concerns instead of duplicating logic in many handlers.
- Keep templates, public files, and assets in their expected HTTP folders.
- Keep Jinja templates under `http/views/`.
- Keep browser-served files under `http/public/`.
- Keep packaged static assets under `http/public/assets/` unless the app already documents a different asset pipeline.

## Database Conventions

- Register database connections through provider helpers, using config-provided connection maps and defaults.
- Register models, tables, and seeders explicitly in the provider.
- Prefer package indexes such as module `__init__.py` exports for models and tables when possible.
- Keep table definitions, models, and seeders in their dedicated package folders.
- Let Uvicore manage topological ordering for related tables instead of hand-ordering foreign key dependencies in scattered code.
- Put SQLAlchemy table definitions under `database/tables/`.
- Put seed logic under `database/seeders/`.
- Put ORM model classes under `models/`.
- When adding a new model-backed feature, update provider registration instead of relying on import side effects.

## Dependency Conventions

- In Poetry, depend on `uvicore` with explicit extras needed by the app, such as `database`, `redis`, or `web`.
- For local framework development, prefer a Poetry path dependency during active framework work.
- Keep test dependencies pinned or narrowly constrained to reduce breakage.

## Preferred Workflow For New Uvicore App Features

- Start by deciding whether the feature is CLI, API, web, database, or a shared service.
- Add or update config first when prefixes, connections, drivers, or behavior toggles are involved.
- Register the feature in the package provider during `boot()`.
- Place logic in the expected package folders instead of inventing parallel structure.
- Use Uvicore services such as config, events, cache, db, redis, mail, and auth through the framework patterns already present.
- When adding reusable behavior, favor modular package design so the app can consume it cleanly.
- For a new runnable app, generate or expect these entrypoints first: `package/bootstrap.py`, `package/provider.py`, `config/app.py`, and `http/server.py` if the app serves web or API traffic.
- For a new CLI feature, add the command module, register it in the provider, and ensure the group name fits the app's existing CLI shape.
- For a new HTTP feature, add route registration, handler/controller code, and any view/public/asset registration needed by the provider.
- For a new database feature, add tables, models, and seeders together when the feature needs all three.

## Anti-Patterns To Avoid

- Do not put heavy startup work in `register()`.
- Do not hardcode runtime configuration that belongs in config files or environment variables.
- Do not bypass provider registration with one-off setup code unless the framework already expects it.
- Do not mix web, API, CLI, and database concerns into one module.
- Do not register commands, routes, or models in arbitrary locations when a provider helper exists.
- Do not create nonstandard folder layouts when the existing package layout already expresses the convention.

## When Generating Code

- Match existing Uvicore naming, module paths, and folder layout.
- Prefer examples consistent with the sample app structure.
- When unsure, choose the more modular, provider-driven approach.
- Explain Uvicore changes in terms of package, provider, config, and registration flow.
- If asked to scaffold a Uvicore app, generate code that follows the sample app's package layout and registration style instead of inventing a simpler but non-Uvicore structure.
- If asked to add a feature, include the provider and config changes required to make the feature actually load, not just the feature module itself.
