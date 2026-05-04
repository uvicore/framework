---
description: "Use when changing Uvicore framework behavior in a breaking, deprecated, renamed, or user-visible way. Covers updating release notes, version changelog pages, and upgrade guides in the docs epologue so framework changes stay documented."
name: "Uvicore Release Notes Conventions"
---
# Uvicore Release Notes Conventions

Use these rules when a framework change is breaking, deprecated, renamed, or significant enough that users need release guidance.

## Update Trigger

- Update release documentation when framework behavior changes in a user-visible way.
- Update release documentation when config keys, provider expectations, route patterns, CLI usage, database behavior, ORM APIs, exceptions, or package lifecycle semantics change.
- Update release documentation when methods are removed, renamed, deprecated, or replaced.

## Required Docs Updates

- Update `docs/docs/epologue/release-notes.md` with the high-level version summary when the change matters for the release narrative.
- Update or create the appropriate versioned changelog page under `docs/docs/epologue/changelog/`.
- Update or create the appropriate upgrade guide under `docs/docs/epologue/upgrade/` when users need migration steps.

## Upgrade Guide Rules

- If users must change application code, config, imports, command usage, or runtime assumptions, add upgrade guidance.
- Include before-and-after examples when the migration is not trivial.
- State exactly what changed and what users must do.

## Anti-Patterns To Avoid

- Do not land breaking framework changes without corresponding epologue updates.
- Do not hide deprecations only in code comments.
- Do not update release notes without updating upgrade docs when user action is required.
