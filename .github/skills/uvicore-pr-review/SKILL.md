---
name: uvicore-pr-review
description: 'Review Uvicore changes for code risks, missing tests, missing docs, and missing release-note or upgrade updates. Use for framework, sample-app, or multi-repo Uvicore reviews where completeness across code, tests, docs, and epologue matters.'
argument-hint: 'Describe the Uvicore change, PR, or review target'
user-invocable: true
---

# Uvicore PR Review

Use this skill when the task is to review a Uvicore change holistically, not just to inspect one file in isolation.

## When To Use

- Review a framework PR or local change set before merge.
- Review a sample-app change that should stay aligned with framework conventions.
- Review changes that affect provider wiring, config, HTTP, CLI, database, docs, or release guidance.
- Audit whether a user-visible or breaking change is missing tests or docs.

## Outcome

Produce a review that checks:

- code correctness and integration risks
- missing or weak tests
- missing documentation updates
- missing release notes, changelog, or upgrade guidance for breaking or notable changes

## Procedure

1. Identify which workspace roots are affected: framework, sample-app, docs, or a combination.
2. Inspect the changed files and map the change surface using [review checklist](./references/review-checklist.md).
3. Review code first for bugs, regressions, and wiring issues.
4. Review tests next for missing coverage, especially around provider/config/runtime integration.
5. Review docs expectations next, including section placement and `mkdocs.yml` updates when relevant.
6. Review release-note expectations last for breaking, deprecated, renamed, or notable user-facing changes.
7. Report findings ordered by severity, with missing tests/docs/release work called out explicitly.

## Review Rules

- Default to a code-review mindset: findings first, summary second.
- Prefer concrete review findings over generic advice.
- Treat provider wiring, config changes, route registration, command registration, model/table/seeder registration, and runtime behavior as high-risk integration surfaces.
- Treat user-visible behavior changes as likely docs candidates.
- Treat breaking or migration-requiring changes as likely epologue candidates.

## Required Checks

- Does the code follow Uvicore register vs boot responsibilities?
- Is config updated where runtime behavior depends on config?
- Are commands, routes, models, tables, seeders, views, or assets properly registered?
- Are tests present for the changed behavior and wiring?
- Are docs updated in the right docs section?
- Does `docs/mkdocs.yml` need an update?
- Are release notes, changelog, or upgrade docs required?

## References

- [review checklist](./references/review-checklist.md)
- [docs expectations](./references/docs-expectations.md)
