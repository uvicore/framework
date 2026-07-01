---
name: journal-and-adr
description: "Use at the END of any substantive task in this repo (new feature, behavior change, notable refactor, non-trivial fix, doc/skill change) to append a dated journal entry, and WHENEVER you make a significant, hard-to-reverse architectural decision to also write an ADR. Covers the journal/ and adr/ folder conventions, the entry templates, ADR numbering and the supersede rule, and the repo-vs-machine-local knowledge principle. Invoke before finishing work so durable reasoning lands in the repo, not just in chat."
user-invocable: true
---

# Journal & ADR — recording durable knowledge in this repo

This repo keeps two lightweight, committed records so reasoning survives beyond a single chat and
reaches teammates on other machines:

- **`journal/`** — a dated narrative of substantive work (the *what & why*).
- **`adr/`** — Architecture Decision Records for significant, hard-to-reverse calls.

Both live at the **repo root** and are **committed**. They are the repo-local complement to Claude's
machine-local memory — see "Where knowledge lives" at the bottom.

## When to write

**Append a journal entry at the END of any substantive task** — a new feature, a behavior change, a
notable refactor, a non-trivial bug fix, or a docs/skill change. Skip trivia (typos, formatting,
purely mechanical renames).

**Also write an ADR** when that task involved a *significant, hard-to-reverse decision* — a choice a
future maintainer will want the *why* for (a new dependency, a public-API or data-model change, a
cross-repo contract, dropping or replacing a library). Most tasks need only a journal entry; an ADR
is the exception. When you write one, link it from the journal entry's **Related** line.

> In the framework, the `uvicore-ship-framework-change` skill's checklist already requires a journal
> entry and (if the change was an architectural call) an ADR — this skill is the how-to for both.

## Journal — how

- **One file per day**: `journal/YYYY-MM-DD.md`. Append each piece of work as an `##` (H2) entry;
  create the file if today's doesn't exist yet.
- Use today's real date (the harness provides it). Don't back- or post-date.
- Record the *reasoning*, not just the diff — a reader should understand **why** the change was made.
- **Cross-repo work**: if the change also touched a sibling repo in the constellation (the framework,
  an upstream/downstream lib, or the `docs`/`schematic` repos), note it under **Related** so a reader
  here knows there were downstream effects. Each repo keeps its own journal — add an entry in the
  other repo too if the work there was substantive.

### Entry template

```markdown
## <Short title>
- **Intent:** what was asked / the goal
- **Changed:** what changed and *why* (the reasoning, not just the file list)
- **Files:** key files touched
- **Related:** ADRs, tests, cross-repo edits, follow-ups
```

## ADR — how

- **Filename**: `adr/NNNN-kebab-title.md` — zero-padded, sequential (`0001-…`, `0002-…`). Pick the
  next number after the highest existing file; the index lives in `adr/README.md`.
- **Format**: compact Nygard — Status, Date/version, Context, Decision, Consequences.
- **Never rewrite history.** When a later decision changes an earlier one, write a NEW ADR and mark
  the old one `Superseded by ADR-NNNN` (leave its content intact).
- **Update `adr/README.md`'s index** with a one-line link to the new ADR.

### ADR template

```markdown
# ADR NNNN: <Title>

- **Status:** Accepted | Proposed | Superseded by ADR-NNNN
- **Date / version:** YYYY-MM-DD (or uvicore X.Y.Z)

## Context
What forces / constraints / problem led to this?

## Decision
What we decided to do.

## Consequences
Trade-offs, what becomes easier/harder, migration impact, what to watch.
```

## Where knowledge lives (repo vs. machine-local)

These repos are worked on by **dozens of team members across many machines**, and each is its **own
git repo**. So **all shared/durable knowledge goes in the repo** — `CLAUDE.md`, `.claude/skills/`,
`docs/`, and the `journal/` + `adr/` here. Claude's `~/.claude/.../memory/` is **per-machine and
per-user** (not committed, not synced): fine for Claude's private working notes, but **never** the
home for anything a teammate or another machine would need. If something there turns out to be
broadly useful, promote it into the repo (a journal entry, an ADR, a skill, or `CLAUDE.md`).
