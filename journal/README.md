# Journal — Framework

A dated, chronological log of substantive work in **this repo**. Lighter than the epologue
changelog, more technical: it records *what changed and why* (the reasoning behind a change), not
just the diff. It is the running narrative that complements the formal release docs and the ADRs.

- **One file per day**: `journal/YYYY-MM-DD.md`. Append each piece of work as an `##` (H2) entry.
- **Update at the end of any substantive task** (new feature, behavior change, notable refactor,
  doc/skill change). Skip trivia (typos, formatting).
- **Cross-repo work**: note edits made in the sibling `docs`/`schematic` repos under **Related**, so
  a reader here knows the change had downstream effects (each repo also keeps its own journal).

## Entry template

```markdown
## <Short title>
- **Intent:** what was asked / the goal
- **Changed:** what changed and *why* (the reasoning, not just the file list)
- **Files:** key files touched
- **Related:** ADRs, tests, cross-repo edits, follow-ups
```

Significant, hard-to-reverse *decisions* also get an [ADR](../adr/README.md) — link it from the
entry's **Related** line.
