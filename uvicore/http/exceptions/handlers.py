from uvicore.http import response
from uvicore.http import Request
from uvicore.http.exceptions import HTTPException
from uvicore.support.dumper import dump


async def api(request: Request, e: HTTPException) -> response.JSON:
    """Main exception handler for all API endpoints"""

    # Get error payload (smart based on uvicore or starlette HTTPException)
    (status_code, detail, message, exception, extra, headers) = _get_payload(e)
    return response.JSON(
        {
            "status_code": status_code,
            "message": message,
            "detail": detail,
            "exception": exception,
            "extra": extra,
        }, status_code=status_code, headers=headers
    )


async def web(request: Request, e: HTTPException) -> response.HTML:
    """Main exception handler for all Web endpoints"""

    # Get error payload (smart based on uvicore or starlette HTTPException)
    (status_code, detail, message, exception, extra, headers) = _get_payload(e)

    try:
        # Try to respond with a errors template, if exists
        return await response.View('errors/' + str(status_code) + '.j2', {
            'request': request,
            **e.__dict__,
        })
    except:

        try:
            # Try to respond with a catch_all template, if exists
            # Uvicore does not have one, but mreschke/themes which is usually included with a package DOES!
            return await response.View('errors/catch_all.j2', {
                'request': request,
                **e.__dict__,
            })
        except:
            # Errors status_code or catch_all template does not exist, response with generic HTML error
            html = f"""
            <div class="error">
                <h1>{status_code} {message}</h1>
                <p>{detail or ''}</p>

                <h3>Exception:</h3>
                <p>{exception or ''}</p>

                <h3>Extra:</h3>
                <pre>{extra or ''}</pre>
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
    exception = None
    if (hasattr(e, 'message')):
        # Error called using uvicores new and expanded HTTPException
        message = e.message
        exception = e.exception
        extra = e.extra
    else:
        # Error called using starlette HTTPException
        message = e.detail
        extra = None
    return (status_code, detail, message, exception, extra, headers)
