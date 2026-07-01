---
name: uvicore-ship-framework-change
description: "Run this WHENEVER you make a substantive change to the Uvicore framework (new feature, new/changed/removed/renamed public API, new config key, new CLI/event/job, or any user-observable behavior change) — ideally before you consider the change done. A framework code change is NOT complete until its matching TESTS and DOCS are updated. Docs means both the relevant docs/docs feature page(s) AND the epologue trio: release-notes, the major-version changelog, and the version upgrade guide. Use this because framework changes routinely ship without tests or docs — close that gap every time."
user-invocable: true
---

# Shipping a Framework Change (tests + docs are part of the change)

A change to `~/Code/uvicore/framework` is **not finished** when the code compiles and works. It is
finished when the **tests** and **docs** that describe it are updated too. Claude has a standing
habit of stopping at the code — this skill exists to stop that. Read it (or at least its checklist)
at the **start** of a framework change so you scope tests+docs in, and run the checklist again
before you report the change as done.

## The three repos (fixed, consistent layout on every machine)

| Repo | Path | Role |
|---|---|---|
| Framework | `~/Code/uvicore/framework` | the `uvicore` library — where you make the change |
| Docs | `~/Code/uvicore/docs` | MkDocs site (https://uvicore.io). Content under `docs/docs/` |
| Schematic | `~/Code/uvicore/schematic` | the app scaffold/installer template (app-author facing) |

You can always assume these paths. Don't hunt for them.

## Does this change need the full treatment?

**Yes** — new public method/option/argument, changed signature/default, removed/renamed/deprecated
API, new config key, new relation/field/decorator, new CLI command/event/job, or any behavior an
app author can observe.

**No (code-only is fine)** — internal refactor with identical behavior, typo, comment, a change
fully covered by an existing test and not mentioned in any doc. When unsure, treat it as **Yes**.

## Step 1 — Tests (in `~/Code/uvicore/framework`)

Add/adjust tests alongside the change. Load the `uvicore-testing` skill for the harness details.
- Tests live under `tests/test_<area>/`; the suite boots the **app1** reference app
  (`tests/apps/app1/`) on in-memory SQLite via the `app1` fixture in `tests/conftest.py`. Reuse it.
- If the feature is user-facing, make **app1** actually exercise it (a model/route/command/config),
  so it's covered end-to-end.
- DB/ORM changes → also run the cross-dialect suite: `poetry run ./bin/test-db-integration.sh all`.
- Run `poetry run ./bin/test.sh` and confirm green before moving on.

## Step 2 — Feature docs (in `~/Code/uvicore/docs/docs/`)

Find the page that already covers the subsystem and **edit it** (prefer editing over new pages).
Map topic → folder (this mirrors the docs repo's own CLAUDE.md):

| Topic | Folder |
|---|---|
| Install, config, app/directory structure | `getting-started/` |
| CLI usage, writing commands | `cli/` |
| API, web, middleware, exceptions | `http/` |
| Database, SQLAlchemy, ORM, seeding, recipes | `database/` |
| Providers, IoC, events, jobs, templating, cache, mail, http client, internals | `deeper/` |
| Release notes, changelog, upgrades | `epologue/` (see Step 3) |

Match the house style: `--- / title: / # Title` frontmatter, relative `.md` links, language-tagged
fences, and the **`acme.wiki`** demo namespace in every example (never a real/other namespace).
If you add a new page, wire it into `mkdocs.yml` `nav:` and the parent `index.md` list.

## Step 3 — Epologue (ALWAYS review these three for a user-visible change)

This is the step most often forgotten. For any user-observable or breaking change, update **all
three**, version-aware. Current framework version is in `framework/pyproject.toml` (e.g. `0.4.x`),
so the "major/minor" line is **0.4**. Discover the real filenames with
`ls ~/Code/uvicore/docs/docs/epologue/changelog ~/Code/uvicore/docs/docs/epologue/upgrade`.

1. **`epologue/release-notes.md`** — the high-level, human-readable summary. Add a concise bullet
   for the feature/breaking change.
2. **`epologue/changelog/<major.minor>.md`** — the deep, version-specific detail (e.g.
   `changelog/0.4.md`). This is where the real "what changed and why" lives.
3. **`epologue/upgrade/from-<old>-to-<new>.md`** — the migration guide for that version jump (e.g.
   `upgrade/from-0.3-to-0.4.md`). **Only when the change is breaking / requires app-author action**
   (removed/renamed API, changed default, required new step). Give the before→after.

If the change is purely additive and non-breaking, (1) and (2) usually suffice; (3) is for breaking
changes only.

## Step 4 — Schematic (in `~/Code/uvicore/schematic`) — when app-author surface changed

If the change alters what an app author writes (model/route/command patterns, config files,
generators, recommended idioms), update the matching `schematic/.claude/skills/*/SKILL.md` and any
affected stub/scaffold files so generated apps and their guidance stay correct.

## Step 5 — Validate the docs build

From `~/Code/uvicore/docs`: `poetry run mkdocs build --strict` must exit 0. It does **not** fail on
bad links — scan the output for `absolute link` / `unrecognized relative link` INFO lines and fix
them (links must be relative, with the `.md` extension).

## Final checklist (run before calling the framework change done)
- [ ] Tests added/updated under `tests/test_<area>/`; app1 exercises it if user-facing; suite green.
- [ ] DB/ORM change → cross-dialect integration suite run.
- [ ] Relevant `docs/docs/<section>/` feature page updated (or added + wired into `mkdocs.yml`).
- [ ] Examples use the `acme.wiki` namespace and house style.
- [ ] `epologue/release-notes.md` bullet added.
- [ ] `epologue/changelog/<major.minor>.md` detail added.
- [ ] Breaking? `epologue/upgrade/from-<old>-to-<new>.md` migration steps added.
- [ ] App-author surface changed? `schematic` skills/stubs updated.
- [ ] `poetry run mkdocs build --strict` exits 0 with no bad-link INFO lines.
- [ ] **Journal entry** appended to `journal/YYYY-MM-DD.md` (intent / what changed & why / files);
      add the same in any sibling repo you edited (`docs`, `schematic`).
- [ ] **ADR** written under `adr/` if this was a significant, hard-to-reverse decision.
- [ ] Version bumped in `pyproject.toml` + `uvicore/__init__.py` if releasing.
