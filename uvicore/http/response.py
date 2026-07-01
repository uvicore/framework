import re
import math
import uvicore
from os import stat
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from uvicore.support.dumper import dump
from uvicore.support.module import load
from uvicore.http.request import Request
from starlette.templating import _TemplateResponse
from prettyprinter import pretty_call, register_pretty
from starlette.background import BackgroundTask as _BackgroundTask
from typing import Any, List, Generic, TypeVar
from uvicore.typing import Dict

# Proxy starlette and fastapi response APIs
# Usage: from uvicore.http.response import FileResponse
#    Or: from uvicore.http import response
#        response.File
# See https://fastapi.tiangolo.com/reference/responses/
from starlette.responses import Response
from starlette.responses import FileResponse, FileResponse as File
from starlette.responses import HTMLResponse, HTMLResponse as HTML
from starlette.responses import JSONResponse, JSONResponse as JSON
from fastapi.responses import UJSONResponse, UJSONResponse as UJSON
from fastapi.responses import ORJSONResponse, ORJSONResponse as ORJSON
from starlette.responses import PlainTextResponse, PlainTextResponse as Text
from starlette.responses import RedirectResponse, RedirectResponse as Redirect
from starlette.responses import StreamingResponse, StreamingResponse as Stream


# Entity Generic
# Pydantic v2 BaseModel is natively generic for Generic OpenAPI schemas
# (the v1 pydantic.generics.GenericModel was removed in v2).
# See https://medium.com/@jkishan421/building-dynamic-api-responses-with-generics-in-fastapi-972fa1f52d54 for details
E = TypeVar("E")


# Get our current template system from the IoC
#templates = uvicore.ioc.make('uvicore.http.templating.jinja.Jinja')
#templates = uvicore.ioc.make('uvicore.http.templating.engine.Templates')
templates = uvicore.ioc.make('uvicore.templating.engine.Templates')
#templates = uvicore.ioc.make('Templates') # Fixme when you impliment other templating engines, if ever


# Cached composer->view matches, a slight performance optimization found by wrk benchmarks
# This is because re.search and load() is expensive, no need to do it over and over.  Just
# do it once for each unique view and cache the found composer modules.
cached_composers: Dict[str, List] = {}


def utc_now():
    """UTC date factory for pydantic Field default_factory on RequestDate"""
    return datetime.now(timezone.utc)


@uvicore.service()
async def View(
    name: str,
    context: dict = {},
    status_code: int = 200,
    headers: dict = None,
    media_type: str = None,
    background: _BackgroundTask = None,
) -> _TemplateResponse:

    # Pull request out of context (which is always present as it is required for response.View())
    request: Request = context.get('request');

    # Convert context into SuperDict so we can merge in view composer context
    context = Dict(context)

    # Get all view composer modules
    composer_modules = []
    if name in cached_composers:
        # Cached composer(s) for this view were found, use the cached module
        #dump('Found cached composer for ' + name)
        composer_modules = cached_composers[name]
    else:
        # No cached composer yet found for this view.  Loop all view composers and re.search
        # the wildcards and dynamically load() the found composers.  If no composer found
        # still set the cache, but set to [] so we never attempt a re.search again
        found = False
        view_name = name.split('.')[0]
        for (composer_module, composer_views) in uvicore.config.uvicore.http.view_composers.items():
            for composer_view in composer_views:
                if (composer_view == '*'): composer_view = '.*'
                if re.search(composer_view, view_name):
                    #dump('Found UNcached composer for ' + name)
                    # Found a view composer matching this view name wildcard
                    found = True

                    # Ensure empty list
                    if name not in cached_composers: cached_composers[name] = []
                    try:
                        # Load the matched composer module, cache the module, but do not instantiate it
                        composer = load(composer_module).object
                        cached_composers[name].append(composer)
                        composer_modules.append(composer)
                    except:
                        # Composer module not found, bad config or missing file, silently ignore
                        pass
                    # Don't 'break' on match because there can be multiple composers matched to a view
        if not found:
            # No matching composer, still set cached_composers so we never try this again as it will NEVER match
            #dump('No composer cound, adding blahk [] to cache for ' + name)
            cached_composers[name] = []

    # Load all composers that match this view and merge in context
    for composer_module in composer_modules:
        # Load composer and merge the return using .defaults() to ensure
        # the view wins in the override battle over the composer
        composer = composer_module(request, name, context, status_code, headers, media_type)
        context.defaults(await composer.compose())

    #dump(name, cached_composers, composer_modules)

    # Render the template
    return templates.render_web_response(
        name=name,
        context=context,
        status_code=status_code,
        headers=headers,
        media_type=media_type,
        background=background
    )


@uvicore.service()
class APIResponse(BaseModel, Generic[E]):
    """Uvicore API Response"""
    # Careful, the text in """ above shows up in OpenAPI docs!
    # Pydantic v2: BaseModel is natively generic (the v1 GenericModel was removed).
    # Optional[x] no longer implies a default in v2, so every optional field needs
    # an explicit = None (or other default) to stay optional.
    api_version: str | None = "1"
    request_date: datetime | None = Field(default_factory=utc_now)
    response_date: datetime | None = None
    response_ms: int | None = None
    paged_response: bool = False
    result_count: int | None = 0
    total_count: int | None = 0
    page_num: int | None = 0
    total_pages: int | None = 0
    data: E | None = None

    @staticmethod
    def begin() -> 'APIResponse':
        return APIResponse()

    @staticmethod
    def start() -> 'APIResponse':
        return APIResponse()

    @staticmethod
    def create() -> 'APIResponse':
        return APIResponse()


    def render(self, data: E, *, total_count: int | None = None, page: int = 0, page_size: int = 0):
        """Render the API Response"""
        self.api_version = uvicore.config('app.api.version') or "1.0"
        self.response_date = utc_now()
        self.response_ms = int((self.response_date - self.request_date).total_seconds() * 1000)
        # If total_count is passed, we are using a paged response
        if total_count is not None:
            self.paged_response = True
            self.total_count = total_count
            self.page_num = page
            self.total_pages = math.ceil(total_count / page_size) if page_size > 0 else 0
        if isinstance(data, list): self.result_count = len(data)
        self.data = data
        return self

    def build(self, data: E, *, total_count: int | None = None, page: int = 0, page_size: int = 0):
        """Alias to render()"""
        return self.render(data=data, total_count=total_count, page=page, page_size=page_size)

    def send(self, data: E, *, total_count: int | None = None, page: int = 0, page_size: int = 0):
        """Alias to render()"""
        return self.render(data=data, total_count=total_count, page=page, page_size=page_size)

    def __call__(self, data: E, *, total_count: int | None = None, page: int = 0, page_size: int = 0):
        """Alias to render()"""
        return self.render(data=data, total_count=total_count, page=page, page_size=page_size)


@uvicore.service()
class APIErrorResponse(BaseModel):
    """Uvicore API Error Response"""
    # Careful, the text in """ above shows up in OpenAPI docs!
    # Remember exception is REMOVED if not running in app.debug=True mode!
    # Pydantic v2: Optional[x] requires an explicit default to remain optional.
    status_code: int | None = None
    message: str | None = None
    detail: str | None = None
    exception: str | None = None
    extra: Any | None = None


@register_pretty(APIResponse)
def pretty_entity(value, ctx):
    return pretty_call(ctx, APIResponse, **value.__dict__)

# @register_pretty(APIResult)
# def pretty_entity(value, ctx):
#     return pretty_call(ctx, APIResult, **value.__dict__)

@register_pretty(APIErrorResponse)
def pretty_entity(value, ctx):
    return pretty_call(ctx, APIErrorResponse, **value.__dict__)
