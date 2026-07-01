# ADR 0006: Composite (multi-column) relation keys

- **Status:** Accepted
- **Date / version:** uvicore 0.4.x (2026-06-23; feature in working tree)

## Context

ORM relations originally joined on a **single** column pair (`local_key` on this table =
`foreign_key` on the related table). Sharded / distributed databases like **Vitess / PlanetScale**
route a query to a single shard using a **shard key** (vindex). A join that omits the shard key
forces a cross-shard scatter/gather, which is slow and is frequently rejected or times out. To run
on those backends, every join must include the shard key columns *in addition to* the natural key —
i.e. a multi-column `ON` clause.

## Decision

`foreign_key` and `local_key` accept **either a single column name or an ordered list of column
names**. When lists are given, the relation builds a multi-column JOIN `ON` clause, pairing columns
**by position** (`local_key[i]` ↔ `foreign_key[i]`) and `AND`-ing them in declared order. A plain
string remains the one-element case, so existing relations are unchanged.

Implementation lives in `uvicore/orm/fields.py` (`Relation.local_keys()` / `foreign_keys()` /
`key_pairs()`), and is honored everywhere a relation is used: eager-loading (`.include()`), the
inline join for `*One` relations, the secondary query for `*Many` relations, and the in-memory
matching that stitches children back to parents.

## Consequences

- **+** Relations work on sharded backends; list the shard key columns first.
- The two lists must be the **same length** — a clear exception is raised otherwise.
- Composite keys are **not derived**; every column must be listed explicitly on both sides.
- Backward compatible: single-string keys behave exactly as before.
- Documented in `docs/docs/database/orm-querybuilder.md` (Composite Relation Keys), with shorter
  call-outs in `orm-model.md`, `db-queries.md`, and `db-sa-queries.md`; PlanetScale/Vitess recipe at
  `docs/docs/database/recipes/planetscale.md`.
