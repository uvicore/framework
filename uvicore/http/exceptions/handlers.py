from uvicore.http import response
from uvicore.http import Request
from starlette.exceptions import HTTPException
from uvicore.support.dumper import dump


async def api(request: Request, e: HTTPException) -> response.JSON:
    """Main exception handler for all API endpoints"""

    # Defined in the running app config api.exceptions.main
    headers = getattr(e, "headers", None)
    return response.JSON(
        {
            "status_code": e.status_code,
            "message": e.message,
            "detail": e.detail,
            "extra": e.extra,
        }, status_code=e.status_code, headers=headers
    )


async def web(request: Request, e: HTTPException) -> response.HTML:
    """Main exception handler for all Web endpoints"""

    # Defined in the running app config api.exceptions.main
    headers = getattr(e, "headers", None)
    dump(e.__dict__)
    try:
        # Try to response with a errors template, if exists
        return response.View('errorsx/' + str(e.status_code) + '.j2', {
            'request': request,
            **e.__dict__,
        })
    except:
        # Errors template does not exist, response with generic HTML error
        html = f"""
        <div class="error">
            <h1>{e.status_code} {e.message}</h1>
            {e.detail or ''}
        </div>
        """
        return response.HTML(
            content=html,
            status_code=e.status_code,
            headers=headers
        )


#async def handle_404(request: Request, exc: HTTPException)
