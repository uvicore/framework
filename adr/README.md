# Architecture Decision Records (ADRs)

One file per **significant, hard-to-reverse decision** about the framework — the kind of choice a
future maintainer will want the *why* for. Day-to-day work goes in the [journal](../journal/README.md);
ADRs capture the durable architectural calls.

- **Filename**: `NNNN-kebab-title.md` (zero-padded, sequential — `0001-...`, `0002-...`).
- **Format** (compact [Nygard](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)):
  Status, Date, Context, Decision, Consequences.
- **Don't rewrite history**: when a later decision changes an earlier one, add a new ADR and mark the
  old one `Superseded by ADR-XXXX` (leave its content intact).

## Template

```markdown
# ADR NNNN: <Title>

- **Status:** Accepted | Proposed | Superseded by ADR-XXXX
- **Date / version:** YYYY-MM-DD (or uvicore X.Y.Z)

## Context
What forces / constraints / problem led to this?

## Decision
What we decided to do.

## Consequences
Trade-offs, what becomes easier/harder, migration impact, what to watch.
```

## Index
- [0001 — Expanded SQL dialect support, driver/port defaults & WHERE operators](0001-expanded-sql-dialects-and-where-operators.md)
- [0002 — Modernize the web stack: Pydantic v2, FastAPI 0.137, Starlette 1.3](0002-modernize-web-stack-pydantic-v2.md)
- [0003 — Central model rebuild (Pydantic v2 forward references)](0003-central-model-rebuild.md)
- [0004 — Standardize on httpx, drop aiohttp](0004-httpx-over-aiohttp.md)
- [0005 — Pipe-style typing convention & Python 3.12 minimum](0005-pipe-style-typing-and-python-floor.md)
- [0006 — Composite (multi-column) relation keys](0006-composite-multi-column-relation-keys.md)
