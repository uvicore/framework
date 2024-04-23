from os import stat
import re
import uvicore
from uvicore.typing import Dict, List
from uvicore.support.dumper import dump
from uvicore.support.module import load
from uvicore.http.request import Request
from starlette.templating import _TemplateResponse
from starlette.background import BackgroundTask as _BackgroundTask

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


# Get our current template system from the IoC
#templates = uvicore.ioc.make('uvicore.http.templating.jinja.Jinja')
#templates = uvicore.ioc.make('uvicore.http.templating.engine.Templates')
templates = uvicore.ioc.make('uvicore.templating.engine.Templates')
#templates = uvicore.ioc.make('Templates') # Fixme when you impliment other templating engines, if ever

# Cached composer->view matches, a slight performance optimization found by wrk benchmarks
# This is because re.search and load() is expensive, no need to do it over and over.  Just
# do it once for each unique view and cache the found composer modules.
cached_composers: Dict[str, List] = {}

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
