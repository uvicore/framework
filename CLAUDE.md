# Uvicore Framework — Developer Guide (CLAUDE.md)

This is the **Uvicore Framework** source repo (`uvicore` Python package, v0.4.1). Uvicore is
a fullstack **async** Python framework for Web, API, and CLI apps — "the performance of
FastAPI with the elegance of Laravel". This file is for developers **enhancing the framework
itself**, not for building apps on top of it.

> Sibling repos (symlinked one level up): `../docs` (MkDocs site, branch `0.3`) and
> `../schematic` (the app scaffold/installer template, branch `0.4`). This repo is `0.4-develop`.
> Docs may lag the 0.4 code.

## Skills — load the right one before working

Specialized skills live in `.claude/skills/`. **Read the matching skill before editing that
subsystem** — they carry the real API surface, file:line references, and the conventions that
keep changes from breaking the bootstrap/IoC contract.

| Skill | Use when working on… |
|---|---|
| `uvicore-architecture` | bootstrap, IoC container, Application, Package, Provider, decorators, the service/binding lifecycle. **Read this first if you're new to the codebase or touching core.** |
| `uvicore-orm-dev` | `uvicore/orm/` — Model, ModelMetaclass, Field, relations, the ORM query builder, mapper. |
| `uvicore-http-dev` | `uvicore/http/` — routing, controllers, AutoApi/ModelRouter, Guard/auth scopes, servers, responses, middleware. |
| `uvicore-database-dev` | `uvicore/database/`, `uvicore/configuration/`, `uvicore/typing/` — the `db` service, low-level query builder, Table, seeders, connections, config system, the `Dict`/SuperDict type. |
| `uvicore-console-events-jobs-dev` | `uvicore/console/`, `uvicore/events/`, `uvicore/jobs/` — CLI commands, schematic generators, the event dispatcher, jobs. |
| `uvicore-testing` | writing/running framework tests (`tests/`, `tests/apps/app1`, `bin/test*.sh`). |
| `uvicore-add-subsystem` | adding a brand-new framework package/service (provider + mixin + IoC binding + config + tests). |

There are also legacy GitHub Copilot instructions in `.github/` that are **app-author** oriented
(how to build apps *on* Uvicore). They're useful background but the `.claude/` skills above are
the framework-development source of truth.

## The one mental model that explains everything

Uvicore is built on an **IoC container** + a **package/provider lifecycle**. Almost every class
is bound into the container by a decorator and resolved lazily by name. Understanding this is
the key to the whole codebase.

### Bootstrap flow (`uvicore/__init__.py` → `uvicore/foundation/application.py`)
1. An app calls `uvicore.bootstrap(app_config, base_path, is_console)` (from its
   `package/bootstrap.py`).
2. `bootstrap()` creates the IoC singleton (`uvicore.ioc`), then sets the `uvicore.app`,
   `uvicore.events`, `uvicore.jobs` globals. **Import order is deliberate** — it lets `app_config`
   override even the earliest core services. Don't reorder it.
3. `Application.bootstrap()` runs:
   - `_build_provider_graph()` — recursively resolves each package's `config/package.py`
     `dependencies`, building an `OrderedDict` of providers. **Last provider definition wins**
     (this is how an app overrides a framework package's provider), while declaration order is
     preserved.
   - `_register_providers()` — instantiates every provider and calls `register()`. Fires
     `uvicore.foundation.events.app.Registered`.
   - `_boot_providers()` — calls `boot()` on every provider. Fires `...app.Booted`.
4. Subsystems that need a fully-merged config (HTTP server, DB connections, console groups)
   **listen for the `Booted` event** and bootstrap themselves then (see
   `uvicore/http/package/bootstrap.py`, `uvicore/database/package/bootstrap.py`,
   `uvicore/console/package/bootstrap.py`).

### register() vs boot() — the cardinal rule
- **`register()`**: config merges (`self.configs([...])`), lightweight IoC bindings, early event
  listeners only. Runs before configs are fully merged — you have **no reliable view of config
  here**. Do NOT do real work.
- **`boot()`**: everything else — register connections, models, tables, seeders, views, routes,
  commands. All configs are deep-merged by now. `self.package` is available (it is `None` in
  `register()`).
- Need to act after *all* packages boot? Listen to the `Booted` event instead of forcing order.

### The IoC container (`uvicore/container/ioc.py`)
- `uvicore.ioc.make(name, default=None, **kwargs)` resolves a binding by name or alias, importing
  the module lazily on first use. Singletons are instantiated once.
- Decorators bind classes: `@uvicore.service()`, `@uvicore.provider()`, `@uvicore.model()`,
  `@uvicore.table()`, `@uvicore.event()`, `@uvicore.job()`, `@uvicore.seeder()`,
  `@uvicore.controller()`/`@uvicore.routes()`, `@uvicore.composer()` (all in
  `uvicore/foundation/decorators/`). Each calls `ioc.bind_from_decorator(...)` with an
  `object_type` tag.
- Default bind name is `{module}.{ClassName}`; pass `aliases=[...]` for short names.
- **Override mechanism** (critical to preserve): the app's `config/app.py` `overrides.ioc_bindings`
  dict (or `provider.bind_override()`) maps a binding name to a replacement module path. When a
  decorator binds a name that has an override, the container binds the override *and* also binds
  the original under `name + '_BASE'` so the override subclass can import its parent without a
  circular import. This is how users swap a framework Table/Model/Provider/Application. Any change
  to binding logic must keep `_BASE` working.

### Globals (set during bootstrap, type-hinted in `uvicore/__init__.py`)
`uvicore.ioc`, `uvicore.app`, `uvicore.events`, `uvicore.jobs`, `uvicore.config`, `uvicore.log`,
`uvicore.cache`, `uvicore.db`. Contracts/interfaces for all of these live in `uvicore/contracts/`.

## Conventions that pervade the codebase
- **Contracts first.** Every service has an ABC interface in `uvicore/contracts/`. When you change
  a public method, update the matching contract.
- **`Dict` / SuperDict everywhere** (`uvicore/typing/dictionary.py`). Config, connections, routes,
  packages are all SuperDicts with `.dotget()`, `.dotset()`, `.merge()` (deep, override wins),
  `.defaults()` (deep, only fills missing), `.clone()`. Missing keys auto-vivify nested Dicts.
  Prefer these over plain dicts to match the codebase.
- **Async by default.** ORM, DB, mail, redis, event/job dispatch, CLI commands are async. Use
  `@pytest.mark.asyncio` in tests.
- **Provider mixins.** Providers compose feature mixins for their `register_*` helpers:
  `console.package.registers.Cli`, `http.package.registers.Http`, `database.package.registers.Db`,
  `redis.package.registers.Redis`, `templating.package.registers.Templating`. See
  `tests/apps/app1/package/provider.py` for the canonical multi-mixin provider.
- **`registers` flags.** A package's `config/package.py` `registers` dict (e.g.
  `{'models': True, 'web_routes': True, ...}`) gates what a provider actually loads. Helper
  methods call `self.package.registers.defaults({...})` then skip work if disabled.
- **Vendored asyncclick.** `uvicore/console/asyncclick/` is a vendored async fork of Click. Don't
  edit it as framework code; treat it as a dependency.
- Files named `OBSOLETE`, `*OLD*`, `archive/`, and large commented-out blocks are dead code —
  ignore them, don't extend them.

## Dev workflow
- **Python ≥3.10**, Poetry, Pydantic **v1.10** (held back — do not use v2 idioms), SQLAlchemy 2.0,
  FastAPI/Starlette for web, `encode/databases`-style async DB layer.
- Extras gate optional deps: `poetry install --extras "database redis web"` (+ `--with test`).
- **Run tests with Poetry, from `framework/`:** `poetry run ./bin/test.sh` (sets
  `PYTHONPATH=./tests/apps`, runs pytest; ~361 tests in a few seconds). Coverage:
  `poetry run ./bin/test-cov.sh` / `poetry run ./bin/test-cov-html.sh`. A single area:
  `poetry run ./bin/test.sh tests/test_orm`.
- The test suite bootstraps the **`app1`** reference app (`tests/apps/app1/`) against an in-memory
  SQLite DB via the `app1` fixture in `tests/conftest.py`. Reuse it; don't invent new bootstrap.
- **Versioning:** bump `pyproject.toml` AND `uvicore/__init__.py.__version__` together (see
  `bin/build.sh`). User-visible/breaking changes should update the docs `epologue` (see the
  release-notes Copilot instruction).
- Formatting: `poetry run ./bin/black-check.sh` (black).

## Directory map (`uvicore/`)
```
foundation/   Application, app lifecycle events, ALL decorators
container/    IoC container (ioc.py) + Binding
package/      Package class + base Provider class
configuration/ Config service + env() helper
contracts/    ABC interfaces for every service (source of truth for public API)
typing/       Dict/OrderedDict SuperDict types
support/      utilities: module load/location, dictionary deep_merge, str, hash, dumper(dump/dd)
orm/          Model, ModelMetaclass, Field, relations, ORM query builder, mapper, drivers
database/     db service, low-level query builder, Table, db CLI commands
http/         routing (web/api/auto_api/model_router/guard), controllers, servers, response, middleware, openapi
console/      CLI command/group decorators, console bootstrap, generators, vendored asyncclick
events/       event Dispatcher, Event base, Handler
jobs/         job Dispatcher, Job base, JobResults
auth/         reference impl: authenticators, user_providers, models, tables, middleware (also a real package example)
cache/        cache manager + array/redis backends
mail/         Mail service + backends
redis/        Redis service
logging/      colored logger + filters
templating/   Jinja2 engine + context functions
```
When in doubt about a real-world pattern, read `tests/apps/app1/` (the canonical app) and the
`auth/` package (a full-featured framework package: provider, config, tables, models, seeders,
http routes, middleware).
