# ADR 0008: Date-stamped log filenames and named log channels

- **Status:** Accepted
- **Date / version:** 2026-07-29 (uvicore 0.4.10)

## Context

Two long-standing limitations of `uvicore.log` surfaced together from real workloads (long-running
Redis/Kafka consumer loops, and apps whose several features each want their own log):

**1. Rename-based rotation is unsafe.** The file handler was always
`logging.handlers.TimedRotatingFileHandler(filename, when, interval, backupCount)`. The commonly
assumed failure — "a long-running loop never rotates" — is **false**: `BaseRotatingHandler.emit`
checks `shouldRollover` on every record, before the write. The genuine failures are worse and less
obvious:

- **Multi-process corruption.** With `uvicorn --workers N` (or a CLI command sharing the server's
  `LOG_FILE_PATH`), processes race on `os.rename`. The loser's `doRollover` hits
  `if os.path.exists(dfn): return` — which returns *without updating `self.rolloverAt`*. That process
  then `shouldRollover() == True` forever (an `os.path.exists` stat per log line), **never rotates
  again**, and keeps appending to a renamed — or `backupCount`-unlinked — inode for the rest of its
  life. Silent, permanent data loss. `backupCount` pruning can also `os.remove` a file a peer process
  still has open.
- **Archives named after the wrong day.** `doRollover` names the archive from
  `rolloverAt - interval`, then recomputes `rolloverAt` from *now*. A process idle Mon→Thu produces
  one archive named for Monday containing four days of records, and no files at all for Tue/Wed.
- The live file has no date, so `ls`/grep/log-shippers need special-casing, and `computeRollover`
  seeds `rolloverAt` from `st_mtime`, so a fresh process against a stale file immediately rotates and
  stamps the archive with an old date.

**2. No way to get more than one log file.** There was exactly one singleton wrapping the stdlib
**root** logger with one console + one file handler. The only naming facility, `.name('uvicore.orm')`,
is a *filter* scope (it feeds `OutputFilter`'s prefix matching), not a destination — and it stored
that scope in a mutable attribute on a singleton, which two concurrent asyncio tasks or two of
FastAPI's `anyio` worker threads can clobber between the `name()` call and the emit.

## Decision

**Date-stamped filenames selected by the configured path.** New stdlib-only
`uvicore/logging/handlers.py` with `DatedFileHandler(logging.FileHandler)`. `build_file_handler()`
picks it when the configured filename contains strftime tokens, and keeps
`TimedRotatingFileHandler` when it does not — so **existing configs are untouched and there is no
migration**. Key design points:

- The check is hooked in **`emit`**, not `_open` (which runs once per stream lifetime and would never
  re-evaluate in the long-running process the feature exists for).
- The filename is derived from **`record.created`**, not `time.time()`, because
  `Formatter.formatTime` renders `%(asctime)s` from `record.created` too. This preserves the one
  invariant that makes dated files worth having: every timestamp inside `2026-07-29_X.log` really
  does start with `2026-07-29`. Rolling is **forward-only** (a record created pre-midnight but
  emitted post-midnight lands in the newer file); per-record bucketing was rejected because a
  stepping clock could thrash the handler open/closed.
- Cost is two int compares per record; `strftime` runs at most once per wall-clock second, and never
  at all for a static path.
- `makedirs(exist_ok=True)` on every resolve (a `%Y/%m/` pattern changes directory on roll, and an
  operator can delete the directory under a live process). The framework previously created none.
- Append mode is enforced; `_reopen` takes only the handler's own RLock (never the module-level
  `logging._lock`, which would deadlock AB-BA against `FileHandler.close()`).
- **`retention` (days, default 0 = forever)** replaces `backupCount`, which *cannot* work with dated
  names because `getFilesToDelete` builds its prefix from today's `baseFilename`. Swept on roll
  (~daily), never per record, against a glob derived from the handler's own pattern so one channel
  can never prune another's files. Deliberately minimal — `logrotate` remains the answer for
  compression/size caps/shipping.

**Named channels with `propagate = False`.** A `channels` config Dict plus
`uvicore.log.channel('Processor')` returning a cached, immutable `Channel`. A shared `LogWriter` base
holds all 20 emit/layout methods plus `dump()`, so `Logger` and `Channel` share the entire surface;
`dump()` needed one line changed (`self._name or 'root'` → `self.logger.name`) to generalize.

`propagate = False` is the crux. The default channel's file handler lives on the **root** logger, and
`Logger.callHandlers` walks the hierarchy firing *every* ancestor handler with no way to address them
individually — so `propagate = True` would write every channel line into the default log file too.
The alternative (a rejecting filter on the root file handler holding a channel registry) was rejected:
it is order-sensitive with lazily-created channels, formats-then-discards every channel record, and
breaks as soon as a channel wants its own console level. With `propagate = False` and each channel
owning its own console+file pair, a record hits its file once and the console once, deterministically.

Supporting decisions:

- **Config lives only in the app's `logger` config** (the cache-manager idiom, not the redis
  `Booted`-bootstrap idiom), because logging registers before any package config merges. `channel()`
  re-reads `uvicore.config('app.logger.channels')` **live** on first access, so a channel added later
  (e.g. from a provider `boot()`) is still honored.
- **Channels inherit `console`/`file` except `filters`/`exclude`.** Those prefix-match `record.name`
  in the framework's naming universe (`uvicore.orm`, `asyncio`); inheriting an include-style
  `filters: ['acme']` would leave every channel file silently empty.
- **Channel names may not contain a dot** — a channel named `uvicore` would become the *parent* of
  `uvicore.orm` and vacuum every ORM record into its file. Raises.
- **Unknown channels auto-create** from defaults rather than raising (unlike `cache.connect()`);
  blowing up on a log call is worse than the typo it would catch.
- **`{channel}` is optional.** If the configured path lacks the token, a named channel gets its name
  appended before the extension (`app1.log` → `app1_Processor.log`). Without this, a user who adds
  channels but forgets the token silently collapses every channel *and* the default log into one
  shared file — defeating the feature with no error. A channel always getting its own file is the
  invariant worth protecting.
- **The default file handler stays on the root logger** so third-party records that propagate up
  (`sqlalchemy`, `databases`, `aiosqlite`, `asyncpg`, `asyncio`, `httpx`, `faker`) keep landing in the
  app's log where the shipped `exclude` lists filter them.
- **`name()`'s scope moved to a `ContextVar`** — per-task and per-thread, no API change.
- The config merge switched from a manual two-level dict splat to `Dict(config).clone().defaults(...)`
  (house convention). **`.clone()` is load-bearing**: `Dict` holds nested SuperDicts by reference and
  `defaults()` mutates in place, so without it constructing a `Logger` would rewrite the live
  `uvicore.config.app.logger`.

## Consequences

- **+** Multiple processes can safely share one log file. This is the headline fix, and it is a
  correctness fix, not a convenience.
- **+** One app can give each feature its own log file with `{}` of config per channel.
- **+** The file handler is finally testable and tested — there was previously *zero* coverage of it.
  42 new tests (11 → 53 in `tests/test_logging/`).
- **+** `explicit import logging.handlers` added; it previously worked only transitively via
  `import logging.config`.
- **Backward compatible.** A path with no strftime tokens behaves exactly as before. The legacy
  `when`/`interval`/`backup_count` keys are retained and still honored for those paths.
- **Retention is opt-in, and `backup_count` silently does not apply to dated paths.** Anyone
  switching to a dated filename without setting `retention` trades bounded disk usage for unbounded.
  Called out in the changelog, upgrade guide and docs page.
- **Dated filenames trade a rename race for a permissions race.** Two different UIDs appending to one
  dated file means `EACCES` → `handleError` per record. Mitigate with a shared group or a `{pid}`
  token. Also, `O_APPEND` write atomicity holds per `write(2)`, so a record exceeding the ~8KB stream
  buffer can still interleave across processes (reachable — uvicore logs whole SQL statements and
  `dump()`s dicts). Both documented.
- **Channels don't reach root handlers.** `caplog`, a Sentry handler, or anything else attached to the
  root logger will not see channel records; attach to `logging.getLogger('<channel>')` instead.
  Documented.
- Channel loggers live in `logging.Logger.manager.loggerDict`, which **never shrinks**. `Channel`
  rebuilds its handler list idempotently, and the test suite has `isolated_logger()` /
  channel-teardown helpers, because otherwise handler duplication leaks across tests and writes every
  line N times.
- Removed the unused `ExcludeFilter` and the dead `uvicore.factories` package (its only member was a
  `Logger` factory never wired as an IoC `factory=`). Neither was referenced anywhere.
- New public contracts `LogWriter` and `LogChannel` alongside `Logger`; `console_handler`/
  `file_handler` annotations corrected from `PythonLogger` to `Handler | None`.
- Extends ADR 0007 (rich console logging), which left the file handler untouched. `RichConsoleHandler`
  and `UVICORE_LOG_THEME` deliberately stayed in `logger.py` so existing imports keep working.
