---
name: uvicore-architecture
description: "Core mental model for the Uvicore framework: the bootstrap sequence, IoC container, Application, Package, Provider lifecycle, the @uvicore decorators, and the IoC override/_BASE mechanism. Read this BEFORE editing anything under uvicore/foundation, uvicore/container, uvicore/package, or any provider/register/boot code, or when you need to understand how services are bound and resolved."
user-invocable: true
---

# Uvicore Architecture (Framework Core)

The whole framework is an **IoC container** plus a **package/provider lifecycle**. Get this right
and the rest of the codebase is obvious. Touching `foundation/`, `container/`, `package/`, or any
`register()`/`boot()` without understanding this WILL break bootstrap or the override system.

## Bootstrap sequence (read the code alongside this)

`uvicore/__init__.py` `bootstrap(app_config, path, is_console)`:
- Order of imports is **load-bearing** (comment says so). It creates `uvicore.ioc = Ioc(app_config)`
  FIRST, then imports `Application`, `Dispatcher` (events), `JobDispatcher` and sets the
  `uvicore.app/events/jobs` globals, then calls `uvicore.app.bootstrap(...)`. Reordering breaks the
  ability of `app_config` to override the earliest core services. Do not touch.

`uvicore/foundation/application.py` `Application.bootstrap()`:
1. Sets `_path`, `_name`, `_main`, debug, and `is_console`/`is_http`/`is_pytest` flags. Special
   cases: `http serve` forces non-console; no `uvicore.http` package forces console;
   `PYTEST_CURRENT_TEST` env forces pytest mode.
2. `_build_provider_graph(app_config)` (`application.py:210`) — recursive: for each package, load
   its `config/package.py`, read `dependencies`, recurse into those first, then record the package
   in `self._providers` (an `OrderedDict`). **Last write wins** but original declaration order is
   preserved → an app can override a framework package's provider by re-declaring it last. Then it
   applies `app_config.overrides.providers`.
3. `_register_providers()` (`application.py:249`) — builds a `Package` object per provider, then
   instantiates the provider via `load(service['provider']).object(...)` and calls `register()`.
   `package=None` is passed here (not available in register). Fires
   `foundation.events.app.Registered`.
4. `_boot_providers()` (`application.py:291`) — re-instantiates each provider WITH its package and
   calls `boot()`. Fires `foundation.events.app.Booted`.
5. Records each package's summary into `running_config`.

## register() vs boot() — the cardinal rule

| | `register()` | `boot()` |
|---|---|---|
| Runs | before configs merged | after ALL packages registered/merged |
| `self.package` | `None` | available |
| Do | `self.configs([...])`, light IoC binds, early `Event.listen()` | connections, models, tables, seeders, views, routes, commands |
| Don't | any real work, anything that reads merged config | — |

Need to run after *every* package has booted (e.g. build the HTTP server from all packages'
routes)? **Listen to the `Booted` event** — do not hand-order providers. The HTTP, database, and
console subsystems all do exactly this in their `package/bootstrap.py`.

## The base Provider (`uvicore/package/provider.py`)

`@uvicore.service(aliases=['PackageProvider','Provider'])` base class. Key methods you'll use/extend:
- `self.configs([{'key':..., 'module':...} | {'key':..., 'value':...}])` — load + deep-merge config
  into `uvicore.config`.
- `self.bind(name, object, *, singleton=False, aliases=[], factory=None, kwargs=None)` — IoC bind,
  honoring app_config `bindings` override.
- `self.bind_override(name, object)` / `self.binding(name)` — override plumbing.
- `self.registers(options)` — set the package's `registers` gate dict.
- Properties: `self.app`, `self.events`, `self.package`, `self.app_config`, `self.package_config`,
  `self.name`.

**Feature `register_*` helpers come from mixins**, not the base provider. A real provider composes
them: `class App1(Provider, Cli, Db, Redis, Http, Templating)` (see
`tests/apps/app1/package/provider.py`). Mixins:
- `console.package.registers.Cli` → `register_cli_commands(...)`
- `http.package.registers.Http` → `register_http_web_routes/api_routes/views/public/assets/...`
- `database.package.registers.Db` → `register_db_connections/models/tables/seeders`
- `redis.package.registers.Redis`, `templating.package.registers.Templating`

## The IoC container (`uvicore/container/ioc.py`)

- `make(name, default=None, **kwargs)` (`ioc.py:91`): resolve by name or alias; lazily
  `module.load()` if unbound; instantiate singletons once (cached on `binding.instance`),
  non-singletons per call (or return the class if no kwargs/factory).
- `bind(name, object, *, object_type='service', override=True, factory, kwargs, singleton, aliases)`
  (`ioc.py:218`): string `object` → stored as `path`, imported lazily; class `object` → path derived
  from `__module__.__name__`. Also usable as a decorator when `object is None`.
- `bind_from_decorator(...)` (`ioc.py:169`): what every `@uvicore.*` decorator calls.
- `bind_override(name, object)` / `overrides` property: merges `_overrides` with
  `app_config.overrides.ioc_bindings` (app config wins).

### Override + `_BASE` (do not break this)
When a decorator binds a name that has an override (`ioc.py:174`):
1. It binds `name` → the override object.
2. It ALSO binds `name + '_BASE'` → the original `cls`, passing the class directly into the binding
   so `.make()` never has to re-import it (this is the circular-import escape hatch). Originals are
   never singletons.

This is how a user swaps a framework `Table`, `Model`, `Provider`, or even `Application`/`Package`
by listing it in `config/app.py` `overrides.ioc_bindings`. The override subclass imports its parent
via the `_BASE` binding. **Any change to binding/decorator logic must preserve `_BASE` and
last-wins ordering.** Live examples: `tests/apps/app1/config/overrides.py` (app1 actively overrides
`Application`, `Provider`, and `Package`), `tests/apps/app1/overrides/`, and the regression suite
`tests/test_ioc/test_overrides.py` — run it after any container/decorator change.

## The decorators (`uvicore/foundation/decorators/`)

All thin wrappers over `ioc.bind_from_decorator(cls, name=..., object_type=..., ...)`:
`provider` (object_type='provider'), `service` (configurable singleton/aliases/factory/kwargs),
`model`, `table`, `event`, `job`, `seeder`, `routes`/`controller`, `composer`. Default bind name is
always `{module}.{ClassName}` unless `name=` is given.

## Globals & contracts
Globals (`uvicore/__init__.py`): `ioc, app, events, jobs, config, log, cache, db`. Every one has an
ABC in `uvicore/contracts/` (`application.py`, `ioc.py`, `provider.py`, `package.py`, `config.py`,
`dispatcher.py`, etc.). **When you change a service's public surface, update its contract too** —
contracts are the documented public API and are tested in `tests/test_contracts/`.

## Pitfalls
- Don't do work in `register()`. If config reads return stale/empty values, that's why.
- Don't reorder the imports in `uvicore/__init__.py.bootstrap()`.
- Don't assume a binding is imported — `make()` imports lazily; a never-`make()`d module's
  decorator never runs. Provider `boot()` explicitly `load()`s model/table modules to fire their
  decorators (see `database/package/bootstrap.py`).
- `self.package` is `None` in `register()`.
- Prefer `uvicore.typing.Dict`/`OrderedDict` over plain dicts (see `uvicore-database-dev`).
