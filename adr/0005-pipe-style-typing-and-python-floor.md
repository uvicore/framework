# ADR 0005: Pipe-style typing convention & Python 3.12 minimum

- **Status:** Accepted
- **Date / version:** Python floor 2026-06-19 (`fcb61eb`); typing convention 2026-06-22 (`35a6ee7`)

## Context

The codebase mixed `typing.Optional[X]` / `Union[...]` with newer syntax, and crossed the boundary
between **`uvicore.typing`** (the framework's `Dict`/SuperDict and re-exports) and the stdlib
`typing` module inconsistently — making signatures noisy and the boundary unclear. Separately, the
minimum supported Python was **3.10**, which held back language/runtime improvements.

## Decision

- **Typing convention**: use pipe-style `X | None` and `A | B` everywhere instead of `Optional` /
  `Union`. Clarify the `uvicore.typing` vs stdlib `typing` boundary (import framework types from
  `uvicore.typing`, language typing constructs from stdlib). Applied repo-wide (~126 files).
- **Python floor**: raise the minimum to **Python 3.12**; verify the suite on **3.12 / 3.13 / 3.14**
  (development on 3.14.6).

## Consequences

- **+** Cleaner, more readable signatures and a clear typing boundary.
- **Drops Python 3.10 / 3.11** — user-visible support change; note in release/upgrade docs.
- Large but mechanical diff; touched ORM (`fields.py`, `query.py`, `metaclass.py`), HTTP routers,
  and `uvicore/typing/__init__.py`.
