from uvicore.http import response
from uvicore.http import Request
#from starlette.exceptions import HTTPException
from uvicore.http.exceptions import HTTPException
from uvicore.support.dumper import dump


async def api(request: Request, e: HTTPException) -> response.JSON:
    """Main exception handler for all API endpoints"""

    # Get error payload (smart based on uvicore or starlette HTTPException)
    (status_code, detail, message, extra, headers) = _get_payload(e)
    return response.JSON(
        {
            "status_code": status_code,
            "message": message,
            "detail": detail,
            "extra": extra,
        }, status_code=status_code, headers=headers
    )


async def web(request: Request, e: HTTPException) -> response.HTML:
    """Main exception handler for all Web endpoints"""

    # Get error payload (smart based on uvicore or starlette HTTPException)
    (status_code, detail, message, extra, headers) = _get_payload(e)

    try:
        # Try to response with a errors template, if exists
        return response.View('errors/' + str(status_code) + '.j2', {
            'request': request,
            **e.__dict__,
        })
    except:
        # Errors template does not exist, response with generic HTML error
        html = f"""
        <div class="error">
            <h1>{status_code} {message}</h1>
            {detail or ''}
        </div>
        """
        return response.HTML(
            content=html,
            status_code=status_code,
            headers=headers
        )

def _get_payload(e: HTTPException):
    """Get error payload depending on uvicore or starlette HTTPException"""
    # Defined in the running app config api.exceptions.main
    headers = getattr(e, "headers", None)

    # Base starletting only has status_code and detail
    status_code = e.status_code
    detail = e.detail
    if (hasattr(e, 'message')):
        # Error called using uvicores new and expanded HTTPException
        message = e.message
        extra = e.extra
    else:
        # Error called using starlette HTTPException
        message = e.detail
        extra = None
    return (status_code, detail, message, extra, headers)
