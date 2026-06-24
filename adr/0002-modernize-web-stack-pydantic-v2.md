# ADR 0002: Modernize the web stack — Pydantic v2, FastAPI 0.137, Starlette 1.3

- **Status:** Accepted
- **Date / version:** 2026-06-19 (uvicore 0.4.0)

> Backfilled from commit `0f51b61`.

## Context

Uvicore was pinned to **Pydantic 1.10**, **Starlette 0.45.3**, and **FastAPI 0.115.7**. FastAPI
**dropped Pydantic v1 in 0.126.0** and **removed the v1 compatibility shim in 0.128.0** — so staying
on Pydantic v1 was a hard ceiling that blocked every modern FastAPI/Starlette release (and their
security/feature updates). The ORM, model router, responses, controllers, and middleware were all
written against v1 idioms.

## Decision

Upgrade the stack to **Pydantic 2.x** (now pinned `2.13.4`), **Starlette 1.3.1**, and
**FastAPI 0.137.2**. Adapt the framework to v2 idioms across the board:
- ORM `metaclass.py` / `model.py` rebuilt for Pydantic v2.
- Serialization `.dict()` → `.model_dump()`; `@validator` → `@field_validator`; explicit defaults on
  optional fields; `on_event` → lifespan `Startup`/`Shutdown` events.
- HTTP `model_router`, `response`, `controllers`, `middleware` updated for the new Starlette/FastAPI.

## Consequences

- **Breaking for application code** — documented in `docs/docs/epologue/upgrade/from-0.3-to-0.4.md`
  and `changelog/0.4.md`.
- Unlocks the modern, maintained web stack.
- Spawned sub-decisions: **central model rebuild** ([ADR 0003](0003-central-model-rebuild.md)) and the
  later **pipe-style typing** cleanup ([ADR 0005](0005-pipe-style-typing-and-python-floor.md)).
- Pydantic is intentionally pinned to `2.x` going forward (no v1 idioms).
