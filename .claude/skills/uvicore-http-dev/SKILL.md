---
name: uvicore-http-dev
description: "Working on the Uvicore HTTP subsystem under uvicore/http/ — routing (WebRouter/ApiRouter/Router), Routes/Controller classes, AutoApi + ModelRouter auto-CRUD, Guard/auth scopes, the base+web+api server build, responses, middleware, and OpenAPI. Read before editing anything in uvicore/http/."
user-invocable: true
---

# Uvicore HTTP Development

Uvicore HTTP wraps **Starlette + FastAPI**. The architecture is one base **Starlette** app with a
**FastAPI** web server and a **FastAPI** API server mounted under it, so web vs API get separate
middleware, exception handlers, and OpenAPI behavior. All of it is assembled on the `Booted` event,
not at import time.

Key files:
- `http/routing/router.py` — base `Router` + `Routes`/`Controller` class; `.controller()`/
  `.include()`/`.group()`; autoprefix logic.
- `http/routing/web_router.py`, `api_router.py` — `WebRouter`/`ApiRouter` (`.get/.post/.put/.patch/
  .delete/.add`).
- `http/routing/auto_api.py`, `model_router.py` — auto-generated REST from ORM models.
- `http/routing/guard.py` — `Guard`/`Scopes` (auth).
- `http/package/bootstrap.py` — the whole server build (read this to understand request flow).
- `http/servers/web.py`, `api.py`, `server.py`, `response.py`, `request.py`, `params.py`,
  `static.py`, `status.py`, `middleware/authentication.py`, `exceptions/handlers.py`,
  `openapi/docs.py`. Contracts: `contracts/router.py`, `contracts/auto_api.py`.

## Defining routes — the Routes/Controller pattern

A package points its provider at a routes module (`register_http_web_routes(module=..., prefix=...)`
/ `register_http_api_routes(...)`). That module is a `Routes` subclass implementing
`register(router) -> router`:

```python
@uvicore.routes()                       # or @uvicore.controller()
class Web(Routes):
    middleware = None                   # class-level; merged into every route
    auth = None
    scopes = None
    def register(self, router: WebRouter):
        router.get('/', Home, name='home')
        router.controller('about')      # str resolves under package controllers path
        return router                   # ALWAYS return the router
```
`router.controller(module, *, prefix, name, tags, options)` (alias `.include()`) mounts a
controller; string resolution: `'home'`→`{controllers}.home.Home`, `'.sub.X'`→`{controllers}.sub.X`,
full path used as-is. `router.group(prefix, *, routes, name, autoprefix, middleware, auth, scopes)`
is both a method and a decorator; child route params override parent on middleware-class match.

`.get(path, endpoint=None, *, name, autoprefix=True, middleware, auth, scopes, inherits)` — same on
Web and Api; **ApiRouter adds** `responses, response_model, response_class, tags, summary,
description`. Routes are stored as **`Dict` (SuperDict) objects**, not dataclasses
(`contracts/router.py` `WebRoute`/`ApiRoute`). `inherits=Fn.getsig` merges a function signature for
DRY shared params.

**Autoprefix** (`router.py`): path becomes `{router.prefix}{path}`, name becomes
`{router.name}.{name}`; disable with `autoprefix=False` to override another package's named route.
Non-GET methods get a method suffix on the name (`name-POST`).

## Auto CRUD — AutoApi + ModelRouter

- `AutoApi` (`auto_api.py`, `@uvicore.service()`): parses JSON query params (`include`, `where`,
  `or_where`, `filter`, `or_filter`, `order_by`, `sort`, `page`, `page_size`, `find`) into an ORM
  query via `.orm_query() -> OrmQueryBuilder`. `guard_relations()` enforces include permissions.
- `ModelRouter` (`model_router.py`, `@uvicore.controller()`): loops all IoC-bound models and
  registers 7 endpoints each — `GET /`, `GET /{id}`, `POST /`, `POST /with_relations`, `PUT /{id}`,
  `PATCH /{id}`, `DELETE /{id}`. Default scopes per model: `{tablename}.{create|read|update|delete}`
  (overridable via `scopes=`/`include=`/`exclude=`).

## Guard / auth scopes (`http/routing/guard.py`)
`Guard(scopes)` subclasses FastAPI `Security` with a `Scopes()` dependency. Validation: user must
have **ALL** listed scopes (AND); **superadmin bypasses**; raises `PermissionDenied`/
`NotAuthenticated`. Usage: `router.get('/x', scopes=['a.read'])` (shorthand), `auth=Guard([...])`,
group/controller-level `scopes`. `request.user: UserInfo` is injected by the auth middleware
(`middleware/authentication.py`) which runs authenticators then falls back to an anonymous user.

## Server build (`http/package/bootstrap.py`, on `Booted`)
`build_package_routes()` → `merge_routes()` → `create_http_servers()` (base=Starlette, web=FastAPI
`openapi_url=None`, api=FastAPI with OpenAPI) → add middleware → add exception handlers →
`add_web_routes()`/`add_api_routes()` (middleware passed as FastAPI `dependencies=`) →
`configure_webserver()` (collect public/asset/view paths + composers from all packages, mount
StaticFiles, init templates) → mount web at web-prefix and api at api-prefix into base.

## Responses (`http/response.py`)
Namespace re-exporting Starlette/FastAPI: `Response, File, HTML, JSON/UJSON/ORJSON, Text, Redirect,
Stream`, plus async `View(name, context, ...)` (runs matching view composers, renders Jinja) and
`APIResponse[E]` generic envelope. Exceptions: `HTTPException(status_code, detail, *, message,
exception, extra, headers)` + `PermissionDenied/NotAuthenticated/InvalidCredentials/NotFound/
BadParameter` (`http/exceptions/`); `exception` (traceback) shown only when `app.debug`.

## Conventions for HTTP changes
- Routes are SuperDicts — read/extend their dynamic keys, don't convert to dataclasses.
- A controller's `register()` must return the router. String controller resolution depends on the
  package's controllers folder; keep it.
- Web and API are deliberately separate servers — don't merge their middleware/handler config.
- Middleware is injected as FastAPI dependencies; matching-class child params override parent
  (don't duplicate).
- Anything needing the full route set must run on `Booted`, not at import.
- Test with the async `client` fixture in `tests/conftest.py`; see `tests/test_http*` and
  `uvicore-testing`.
