# ADR 0003: Central model rebuild (Pydantic v2 forward references)

- **Status:** Accepted
- **Date / version:** 2026-06-19 (uvicore 0.4.0)

> A sub-decision of [ADR 0002](0002-modernize-web-stack-pydantic-v2.md) (the Pydantic v2 migration).

## Context

Uvicore ORM models declare relations whose related types are often **forward references** (quoted
type strings / late imports) to avoid circular imports between related model files. Under Pydantic
**v1**, each model with such forward refs had to call `Model.update_forward_refs()` (typically at the
bottom of the model file, after importing the related types) to resolve them.

Pydantic **v2** renames this: `update_forward_refs()` becomes an alias for `model_rebuild()`. Either
way, requiring every model file to call it is boilerplate that is easy to forget, and a missed call
produces confusing runtime errors only when the relation is first used.

## Decision

Uvicore now **rebuilds every registered model centrally at boot**. App authors no longer add
`update_forward_refs()` / `model_rebuild()` to each model file. They keep:
- `from __future__ import annotations` at the top, and
- the bottom-of-file imports of forward-referenced relation types (so the names are importable when
  the central rebuild runs).

## Consequences

- **+** Removes per-model boilerplate and a whole class of "forgot to rebuild" bugs.
- **+** One consistent place owns model finalization.
- **Breaking for 0.3 apps**: existing models must *delete* their `update_forward_refs()` calls.
  Documented in `docs/docs/epologue/upgrade/from-0.3-to-0.4.md` and `changelog/0.4.md`.
- Forward-ref types must still be importable at boot — the bottom-of-file relation imports remain
  required.
- Docs/scaffold guidance updated to match (ORM docs pages, schematic `uvicore-database` skill).
