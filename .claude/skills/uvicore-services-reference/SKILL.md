---
name: uvicore-services-reference
description: "Quick public-API reference for Uvicore's leaf service subsystems that don't have a dedicated skill — templating (Jinja2), mail, redis, cache, logging, auth (UserInfo/authenticators/guards), and the exception classes (SmartException + HTTP exceptions + status codes). Use when working on or wiring up uvicore/templating, uvicore/mail, uvicore/redis, uvicore/cache, uvicore/logging, uvicore/auth, or uvicore/exceptions."
user-invocable: true
---

# Uvicore Service Subsystems Reference

Verified API surface for the smaller service subsystems (the core ones — orm/http/database/
console — have their own skills). Each is an `@uvicore.service()` resolvable from the IoC and most
have a `uvicore.<x>` global. Always confirm against the source/contract before relying on a detail.

## Templating — `uvicore/templating/engine.py`
`Templates` service (`@uvicore.service('uvicore.templating.engine.Templates', aliases=['Templates',
'templates'], singleton=True)`). Methods:
- `render(template_name: str, data: Dict = {}) -> str` — render to a string (CLI/string use).
- `render_web_response(name, context: dict, status_code=200, headers=None, media_type=None,
  background=None) -> _TemplateResponse` — render to a Starlette response (context must include
  `request`). View composers + `url()`/`asset()`/`public()` context functions are wired here. The
  HTTP `response.View(...)` helper calls this.

## Mail — `uvicore/mail/__init__.py`
`Mail` service (`@uvicore.service()`; `uvicore.ioc.make('Mail')` or `from uvicore.mail import Mail`).
Fluent, chainable builder; config from `uvicore.config.app.mail`:
```python
await (Mail().to([...]).cc([]).bcc([]).from_name(..).from_address(..)
            .subject(..).html(..).text(..).attachments([..]).send())
```
`.mailer(name)` / `.mailer_options({...})` switch driver. Message is a `contracts.Email` SuperDict;
driver loaded dynamically at `send()` from `mailer_options.driver`. Backends in `mail/backends/`.

## Redis — `uvicore/redis/redis.py`
`Redis` service (`aliases=['Redis','redis']`, singleton). Requires the `redis` extra.
- `connection(name=None) -> cfg` — connection config (host/port/database/password/url).
- `async connect(name=None) -> redis.asyncio.Redis` — pooled client (lazy, one pool per URL).
Resolve via `uvicore.ioc.make('redis')`; then full aioredis async command surface.

## Cache — `uvicore/cache/manager.py` + `cache/backends/`
`uvicore.cache` (manager). `connect(store=None)` / `store(store=None)` pick a backend
(`array` in-memory default, `redis`). Backend contract (`contracts/cache.py`, all async):
`has, get(key, default=), put(key, value, seconds=), add, pull, remember(key, callback, seconds=),
touch, increment, decrement, forget, flush`. Config: `config.app.cache`.

## Logging — `uvicore/logging/logger.py`
`Logger` service (`'uvicore.logging.logger.Logger'`, aliases `['Logger','logger','Log','log']`,
singleton) → `uvicore.log`. Levels: `info/notice/warning/debug/error/critical/exception`. Layout
helpers: `header/header2/header3/header4`, `item/item2/item3/item4`, `line/nl/separator/blank`,
`name(str)` for a scoped sub-logger. `ColoredFormatter`, `OutputFilter`/`ExcludeFilter` do
prefix-based include/exclude. Config: `config.app.logger`.

## Auth — `uvicore/auth/`
- **`UserInfo`** (`auth/user_info.py`, Pydantic v2 model, injected as `request.user`): fields
  `id, uuid, username, email, first_name, last_name, title, avatar, groups, roles, permissions,
  superadmin, authenticated, extra`. Computed: `name`, `is_admin`/`admin`/`is_superadmin`,
  `is_authenticated`/`loggedin`/`check`, and the `is_not_*` negations. Methods:
  `can(perms)` (ALL — superadmin bypasses), `can_any(perms)`, `cant`/`cannot`.
- **Authenticators** (`auth/authenticators/`): `base`, `basic`, `jwt`. **User providers**
  (`auth/user_providers/`): `orm`, `jwt`. Wired by the HTTP `Authentication` middleware per
  route-type from `config.app.auth` (see `uvicore-http-dev` for Guard/scope enforcement).
- `Auth` service (`auth/auth.py`) is currently a thin placeholder.

## Exceptions
- **`SmartException`** (`uvicore/exceptions/__init__.py`): dual-mode base —
  `SmartException(detail, status_code=None, message=None, exception=None, extra=None, headers=None)`.
  In HTTP context it behaves as an `HTTPException` (default `status_code=500`); in CLI it's a plain
  exception with an exit-code `status_code` (default `1`). `exception` (traceback) is shown only when
  `config.app.debug`.
- **HTTP exceptions** (`uvicore/http/exceptions/__init__.py`): `HTTPException(status_code, detail, *,
  message, exception, extra, headers)` + `PermissionDenied, NotAuthenticated, InvalidCredentials,
  NotFound, BadParameter`. Rendered by the API/web handlers (`http/exceptions/handlers.py`).
- **Status codes**: `from uvicore.http import status` (e.g. `status.HTTP_200_OK`,
  `HTTP_404_NOT_FOUND`; ~52 constants in `http/status.py`).

## Notes
- These are leaf subsystems — when changing one, read its source + its `contracts/` ABC (the
  documented public surface) and update the contract if the public API changes.
- App-side usage of these same services is documented in the schematic app's
  `uvicore-framework-services` skill.
