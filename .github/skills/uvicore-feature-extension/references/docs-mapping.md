# Uvicore Docs Mapping

Use the docs workspace to keep public guidance aligned with code changes.

## Common Mapping

- CLI command behavior: `docs/docs/cli/`
- HTTP routing, controllers, views, middleware, exceptions: `docs/docs/http/`
- Database and ORM behavior: `docs/docs/database/`
- Provider, IoC, events, jobs, templating, cache, mail, http client: `docs/docs/deeper/`
- Installation or app structure: `docs/docs/getting-started/`
- Breaking changes and upgrades: `docs/docs/epologue/`

## Navigation

- Update `docs/mkdocs.yml` when a new page should appear in site navigation.
- If the page is internal contributor guidance only, keep it in an existing contributor or deeper section rather than adding noisy top-level navigation.
