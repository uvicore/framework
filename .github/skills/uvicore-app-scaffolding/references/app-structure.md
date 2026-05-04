# Uvicore App Structure

## Standard Layout

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
      assets/
    routes/
    views/
    server.py
  models/
  package/
    bootstrap.py
    provider.py
```

## Bootstrap

- `package/bootstrap.py` should find the app base path, load `.env`, import app config, then call `uvicore.bootstrap(app_config, base_path, is_console)`.
- `http/server.py` should bootstrap the app and expose `http = app.http`.

## Provider Lifecycle

- `register()` is for config merges, lightweight bindings, and early listeners only.
- `boot()` is for real registration work after all configs are merged.
- Prefer helper methods from `boot()` such as dedicated `register_views()`, `register_routes()`, and `register_commands()` helpers for readability.

## Registration Order

- `registers()` control
- redis connections
- database connections
- models
- tables
- seeders
- views
- routes
- commands

## Config Shape

- `config/app.py` is the running app config aggregator.
- Keep concern-specific config in modules such as `auth.py`, `cache.py`, `database.py`, `http.py`, `logger.py`, `mail.py`, and `package.py`.
- `main.package` should name the runnable package.
- `main.provider` should point to the provider class.

## HTTP

- Keep web and API route registration separate.
- Put web routes under `http/routes/web.py`.
- Put API routes under `http/routes/api.py`.
- Put API handlers under `http/api/` and web controllers under `http/controllers/` when layered handlers are needed.

## Database

- Put tables under `database/tables/`.
- Put seeders under `database/seeders/`.
- Put ORM models under `models/`.
- Register all of them in the provider.
