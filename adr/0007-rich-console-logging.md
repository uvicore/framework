# ADR 0007: Render console logging with rich (base dependency)

- **Status:** Accepted
- **Date / version:** 2026-07-06 (uvicore 0.4.9)

## Context

`uvicore.log`'s console output was rendered by a hand-rolled `ColoredFormatter` built on the
`colored` library. It decoded prefix conventions the `Logger` layout helpers emit (`:: header ::`,
`## header2 ##`, `* item`, `NOTICE: …`, etc.) and wrapped them in ANSI codes. It worked but was
verbose, hard to extend, and plain-looking. We wanted *much* prettier console output (rules, glyphs,
badges) without changing the public `uvicore.log` interface, without touching the file handler
(logs must stay plain/greppable), and without touching `prettyprinter` (`dump()`/`dd()`).

## Decision

Render **console (STDOUT/STDERR) logging with [rich](https://rich.readthedocs.io/)**:

- Add **`rich==14.2.0` to the base `dependencies`**, deliberately **not** gated behind the
  `web`/`database`/`redis` extras — console output should be beautiful for every install, including
  pure-CLI apps. (Pins its transitive `markdown-it-py`/`mdurl` in the frozen subdependency block.)
- Replace `ColoredFormatter` with a `RichConsoleHandler(logging.Handler)` that keeps the exact same
  prefix semantics and renders them via a tweakable module-level `UVICORE_LOG_THEME`
  (`header`/`header2` → full-width rules; `header3`/`header4` → inline text; items → glyph bullets;
  notice/critical → badges; warning/error → icon prefixes).
- **Split streams:** `WARNING`/`ERROR`/`CRITICAL` → **STDERR**; `DEBUG`/`INFO` + layout helpers →
  **STDOUT** (previously everything went to STDOUT).
- `logger.console.colors = False` falls back to the previous plain, ASCII, STDOUT-only
  `StreamHandler` (no rich) as an escape hatch.
- The `Logger` keeps explicit console/file handler references rather than relying on handler list
  index order, so `console_handler`/`file_handler` and `dump()`'s console-silencing stay correct
  with the new handler type.

The public `Logger`/`uvicore.log` interface (contract in `uvicore/contracts/logger.py`) is
**unchanged**.

## Consequences

- **+** Much richer console output; re-skinnable in one theme dict; rich available framework-wide
  for future console UI (tables, progress bars).
- **+** File logging and `dump()`/`dd()` are untouched — file logs stay plain and greppable.
- **+** `colored` was the logger's *only* consumer, so it was **removed** from the base
  dependencies — the rich addition nets to roughly a wash on footprint (rich + markdown-it-py +
  mdurl in, colored out; `pygments` was already pinned).
- **Behavior change (non-breaking-ish):** anything that captured *only* STDOUT no longer sees
  warning/error lines there — they moved to STDERR. Documented in the 0.4.9 changelog; `colors=False`
  restores the old single-stream plain output.
- Not adopted (yet): rich `progress`/spinner helpers seen in the `vtcman` side project — they'd
  extend the `Logger` contract, so deferred.
