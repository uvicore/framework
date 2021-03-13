import uvicore
from starlette.background import BackgroundTask as _BackgroundTask
from starlette.templating import _TemplateResponse

# Proxy starlette response APIs
#from starlette.responses import Response as Generic
from starlette.responses import Response
from starlette.responses import PlainTextResponse as Text
from starlette.responses import HTMLResponse as HTML
from starlette.responses import JSONResponse as JSON
from starlette.responses import UJSONResponse as UJSON
from starlette.responses import RedirectResponse as Redirect
from starlette.responses import StreamingResponse as Stream
from starlette.responses import FileResponse as File

# Get our current template system from the IoC
templates = uvicore.ioc.make('uvicore.http.templating.jinja.Jinja')

@uvicore.service()
def View(
    name: str,
    context: dict = {},
    status_code: int = 200,
    headers: dict = None,
    media_type: str = None,
    background: _BackgroundTask = None,
) -> _TemplateResponse:
    return templates.TemplateResponse(
        name=name,
        context=context,
        status_code=status_code,
        headers=headers,
        media_type=media_type,
        background=background
    )
