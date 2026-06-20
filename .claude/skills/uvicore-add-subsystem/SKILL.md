---
name: uvicore-add-subsystem
description: "End-to-end workflow for adding a new capability to the Uvicore framework itself — a new bound service, a new framework package (provider + config + mixin), a new provider register_* helper, a new IoC-bound type, or a new CLI/event/job. Use when extending the framework's own feature set (not when building an app on top of Uvicore)."
user-invocable: true
---

# Adding a Subsystem / Service to the Uvicore Framework

Use when you're extending the framework's own capabilities. First read `uvicore-architecture` (the
IoC + provider lifecycle) — everything here builds on it. For app-author scaffolding, use the
legacy `.github` Copilot skills instead.

## Decide the shape

| You want… | Do this |
|---|---|
| A reusable service (mail/redis/cache-like) | `@uvicore.service(..., singleton=?, aliases=[...])` class with an ABC in `contracts/`, bound + initialized by a provider in `boot()`. |
| A whole new framework package (its own folder + provider) | New `uvicore/<name>/` with `package/provider.py`, `config/package.py`, and the feature code. |
| A new `register_*()` helper for providers | Add a method to the subsystem's `package/registers.py` mixin. |
| A new bound type (model/table/event/job/controller) | Use the matching decorator; it auto-binds. |
| A new CLI command / event / job | See `uvicore-console-events-jobs-dev`. |

## Workflow for a new framework package

1. **Folder**: create `uvicore/<name>/` with `__init__.py`, the feature module(s), `contracts` (or
   add to `uvicore/contracts/`), and `package/provider.py`.
2. **Contract**: define the public interface as an ABC in `uvicore/contracts/<name>.py` and export
   it from `uvicore/contracts/__init__.py`. This is the documented API and gets tested.
3. **Service**: implement the class, decorate with `@uvicore.service('uvicore.<name>.<mod>.<Class>',
   aliases=['Name','name'], singleton=True_if_stateful)`. Implement the contract.
4. **Config**: `uvicore/<name>/config/package.py` exporting a `config` dict (use `env(...)` for
   env-driven values; include a `registers` gate if the package conditionally loads things).
5. **Provider** (`uvicore/<name>/package/provider.py`):
   ```python
   @uvicore.provider()
   class Name(Provider):                      # + mixins if it registers cli/http/db/...
       def register(self):
           self.configs([{'key': self.name, 'module': 'uvicore.<name>.config.package.config'}])
           # light IoC binds / early Event.listen() only
       def boot(self):
           self.registers(self.package.config.registers)
           # real init: read merged config, bind+init the service, register commands/routes/etc.
   ```
   - `register()` = config + light binds ONLY. `boot()` = real work. `self.package` is None in
     `register()`.
   - If the subsystem must see *all* packages (e.g. collect routes/connections), do that work in a
     handler listening to `foundation.events.app.Booted` (see `http/`, `database/`, `console/`
     `package/bootstrap.py`), not in `boot()` directly.
6. **Global** (only if it deserves one like `uvicore.db`): add the lazy global + TYPE_CHECKING hint
   in `uvicore/__init__.py` and assign it during the subsystem's bootstrap.
7. **Dependency wiring**: a package is loaded because something depends on it. Add it to a
   `config/package.py` `dependencies` map (framework default chain) or rely on the app listing it in
   `overrides.providers`. Confirm it appears in the provider graph.
8. **Provider mixin** (if other packages should register things into your subsystem): add a
   `package/registers.py` mixin class with `register_<feature>()` methods that write into
   `self.package.<area>` and call `self.package.registers.defaults({...})` to gate it. Follow
   `console/package/registers.py` / `http/package/registers.py`.
9. **Optional deps**: if it needs extra libraries, add them under the right `[project.optional-
   dependencies]` extra in `pyproject.toml` and import defensively (`try/except ImportError`) like
   `foundation/application.py` does for FastAPI/Starlette.
10. **Tests**: add `tests/test_<name>/` and a contract test; wire any fixtures through the `app1`
    fixture. See `uvicore-testing`. Make app1 exercise the feature if it's user-facing.

## Make it overridable (preserve the framework contract)
Anything you bind by name can be swapped by an app via `config/app.py` `overrides.ioc_bindings`. The
container auto-creates the `name + '_BASE'` binding so an override subclass can extend the original.
Don't bypass `@uvicore.*` decorators / `ioc.bind` with import side effects — that breaks overrides.
See `tests/apps/app1/overrides/` for how users override `application`, `package`, `metaclass`,
`model`, `model_router`, etc.

## Checklist before done
- [ ] Contract ABC added/updated in `uvicore/contracts/` and exported.
- [ ] `register()` only merges config / does light binds; real work in `boot()` (or a `Booted`
      listener).
- [ ] Service bound with sensible name + aliases + singleton flag.
- [ ] Config uses `env()`; `registers` gate respected if conditional.
- [ ] IoC binding stays overridable (`_BASE` / decorator path intact).
- [ ] Optional deps gated in `pyproject.toml` and imported defensively.
- [ ] Tests added under `tests/test_<name>/`; app1 updated if user-facing.
- [ ] Public/breaking change → note for docs `epologue` (release notes/upgrade).
- [ ] Version bumped in `pyproject.toml` + `uvicore/__init__.py` if releasing.
