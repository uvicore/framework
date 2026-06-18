---
name: uvicore-console-events-jobs-dev
description: "Working on Uvicore CLI/console, the event dispatcher, or the jobs system — uvicore/console/ (command/group decorators, console bootstrap, schematic generators, vendored asyncclick), uvicore/events/ (Dispatcher, Event, Handler), uvicore/jobs/ (Dispatcher, Job). Read before editing those, or before adding CLI commands, events, or jobs to the framework."
user-invocable: true
---

# Uvicore Console, Events & Jobs Development

## Console / CLI (`uvicore/console/`)

- **Decorators** (`console/decorators.py`, re-exported from `console/__init__.py`): `command()` and
  `group()` wrap the vendored **asyncclick** with colored help (`HelpColorsCommand`/`Group`, yellow
  headers/green options). Also `argument`, `option`, and `asyncclick as click`. Commands are
  **async**:
  ```python
  from uvicore.console import command, argument, option
  @command()
  @argument('name')
  @option('--json', is_flag=True)
  async def cli(name: str, json: bool):
      """Help text shown in CLI"""
  ```
- **Root CLI** (`console/console.py`): bound `@uvicore.service(aliases=['Console','console','cli'])`,
  a `@group` with `@click.pass_context`; dispatches `console.events.command.Startup` on start and
  `Shutdown` on close (and `PytestStartup`/`PytestShutdown` under pytest — the DB layer listens to
  these to connect/disconnect).
- **Registration** (provider, via `Cli` mixin `console/package/registers.py`):
  `self.register_cli_commands(group='app1', help='...', commands={'test':'app1.commands.test.cli'})`
  or pass a full `{group: {help, commands}}` dict. Merges into `package.console.groups`; gated by
  `registers.commands`.
- **Bootstrap** (`console/package/bootstrap.py`, on `Booted`): merges all packages' command groups,
  builds click groups (supports `parent:child` nesting via `:`), `add_command`s each, and attaches
  to the root `cli`. Groups only register when running from console (except `http` which always
  registers).
- **Schematic generators** (`console/commands/generators.py` + `commands/stubs/`): the `gen`
  commands. A generator loads a stub from `stubs/`, computes the destination via
  `package.folder_path(type)`, and runs `support.schematic.Schematic(type, stub, dest,
  replace=[('xx_name', name)]).generate()`. Other packages extend `gen` (HTTP adds
  `gen controller`, ORM adds `gen model`, db adds `gen table`/`gen seeder`). To add a generator: add
  a stub, a `@command()` in that package's `commands/generators.py`, and register it under the `gen`
  group.

## Events (`uvicore/events/`)

- Define with `@uvicore.event()` on an `Event` subclass (`events/event.py`); set `is_async`
  (default `False`). Name auto = `{module}.{Class}`; docstring = description.
- **Listen** (class methods, all aliases of dispatcher `.listen`): `MyEvent.listen(handler,
  priority=50)` (also `.listener/.handle/.handler/.call`). Lower priority runs first. Handlers may
  be callables or classes with `__call__` (a `Handler`, `events/handler.py`); sync handlers invoked
  from async dispatch run in a threadpool.
- **Dispatch**: `MyEvent(...).dispatch()` (sync), `await MyEvent(...).dispatch_async()` / `.codispatch()`
  (async). Or via `uvicore.events.dispatch(event_or_str, payload={})`. Supports **wildcard**
  string listeners (regex-matched in `Dispatcher.event_listeners`).
- The `Dispatcher` (`events/dispatcher.py`) is a singleton set up in bootstrap BEFORE any provider
  (events fire during registration) — it is intentionally **not** a service provider.
- App lifecycle events: `uvicore.foundation.events.app.Registered` and `Booted`
  (`foundation/events/app.py`) — subsystems bootstrap on `Booted`. ORM models fire
  `uvicore.orm-{modelfqn}-BeforeInsert/AfterInsert/BeforeSave/...`.

## Jobs (`uvicore/jobs/`)
- `@uvicore.job()` on a class with an async `handle()` method (`jobs/job.py`). Dispatch:
  `await MyJob(...).dispatch_async()` / `.codispatch()` (or sync `.dispatch()`); the `Dispatcher`
  (`jobs/dispatcher.py`, singleton) just calls `instance.handle()`. Wrap return data in a
  `JobResults` (Pydantic model, `jobs/results.py`) subclass for nice printing.

## Conventions
- CLI commands are async and live in dedicated `commands/<name>.py` modules; register via the
  provider, don't import-and-attach ad hoc.
- Don't edit `console/asyncclick/` as framework code — it's a vendored dependency.
- Events fire during bootstrap, so the dispatcher must stay provider-independent; keep it that way.
- New framework events should be `@uvicore.event()` classes (auto-registered), not raw strings.
- Test under `tests/test_console/`, `tests/test_events.py`, `tests/test_jobs/`. CLI tests use
  asyncclick's test runner; see `uvicore-testing`.
