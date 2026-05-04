---
description: "Use when a Uvicore task spans both a specialized skill and one or more Uvicore instructions. Helps agents decide when to combine skills with docs, testing, release-note, and routing instructions instead of treating them as separate choices."
name: "Uvicore Instruction Routing"
---
# Uvicore Instruction Routing

When working on Uvicore tasks, do not treat skills and instructions as mutually exclusive.

## Core Rule

- Choose the best specialized skill for the primary workflow.
- Then also apply any relevant Uvicore instructions that govern testing, docs, release notes, versioning, docs maintenance, or skill routing for the changed area.

## How To Combine Them

- Use a build or extension skill for the main implementation workflow, then also follow testing instructions when the task adds or changes behavior.
- Use a review skill for the main review workflow, then also follow docs or release-note instructions when the change is user-visible or breaking.
- Use a docs skill for writing or auditing docs, then also follow release-note or versioning instructions when the docs touch the epologue.

## Common Combinations

- `uvicore-app-scaffolding` plus `uvicore-testing.instructions.md` when scaffolding a feature that should ship with tests.
- `uvicore-feature-extension` plus `uvicore-testing.instructions.md` when extending runtime behavior.
- `uvicore-feature-extension` plus docs instructions when the change affects public usage or recommended structure.
- `uvicore-pr-review` plus release-note instructions when reviewing breaking or notable framework changes.
- `uvicore-docs-authoring` plus versioning and release-note instructions when adding changelog or upgrade content.
- `uvicore-docs-qa` plus docs maintenance instructions when new docs may have left stale pages or stale navigation behind.

## Decision Rule

- Skills answer "what workflow should I use?"
- Instructions answer "what rules must still be followed while doing that workflow?"
- If both apply, use both.
