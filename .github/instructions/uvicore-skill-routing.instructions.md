---
description: "Use when a Uvicore task could be handled by one of the repo's specialized skills. Helps agents choose between scaffolding, feature extension, PR review, docs authoring, docs QA, and sample-app review workflows based on task type."
name: "Uvicore Skill Routing"
---
# Uvicore Skill Routing

Before starting a substantial Uvicore task, prefer the most specific Uvicore skill instead of handling the work ad hoc.

## Choose The Right Skill

- Use `uvicore-app-scaffolding` when creating a new Uvicore app surface or a new feature that needs provider/config/routes/models/tables/views/commands wired from scratch.
- Use `uvicore-feature-extension` when modifying an existing Uvicore feature in place without scaffolding a brand new app structure.
- Use `uvicore-pr-review` when reviewing changes for bugs, missing tests, missing docs, or missing release-note and upgrade coverage.
- Use `uvicore-docs-authoring` when the main task is writing or restructuring Uvicore docs pages or MkDocs navigation.
- Use `uvicore-docs-qa` when auditing whether docs, navigation, or epologue updates are missing after code or docs changes.
- Use `uvicore-sample-app-review` when reviewing sample-app changes to see whether the example app still reflects current framework best practices.

## Routing Rule

- Prefer invoking a specialized skill whenever the task clearly matches one of the cases above.
- Fall back to direct handling only when the task is too small to benefit from a skill or when no specialized skill fits.
- If a task spans multiple areas, choose the skill that matches the primary goal first, then use other skills or instructions as supporting context.
