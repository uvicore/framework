# Uvicore Docs Expectations For Reviews

## Section Mapping

- CLI changes: `docs/docs/cli/`
- HTTP changes: `docs/docs/http/`
- Database and ORM changes: `docs/docs/database/`
- Provider, modularity, IoC, templating, events, jobs, cache, mail, http client: `docs/docs/deeper/`
- App structure and installation changes: `docs/docs/getting-started/`
- Release summary, changelog, upgrade guidance: `docs/docs/epologue/`

## Release Triggers

Look for missing release-note updates when a change:

- breaks compatibility
- deprecates or removes behavior
- renames user-facing APIs, config, commands, or workflow
- changes defaults users depend on
- requires code or config migration during upgrade
