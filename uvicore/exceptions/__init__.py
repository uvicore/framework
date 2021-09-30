import uvicore
from uvicore.typing import Any, Dict, Optional

# Smart exception should work regardless
has_http = True
try:
    from uvicore.http.exceptions import HTTPException as BaseException
    #from starlette.exceptions import HTTPException as BaseException
except ImportError as e:  # pragma: nocover
    BaseException = Exception
    has_http = False


class SmartException(BaseException):
    # Notice detail and status_code are reversed from my uvicore.http.exceptions.HTTPException
    # This is intentional as SmartExceptions are used as a mix of CLI and HTTP
    def __init__(self,
        detail: Optional[str],
        status_code: int = None,
        *,
        message: Optional[str] = None,
        exception: Optional[str] = None,
        extra: Optional[Dict] = None,
        headers: Optional[Dict[str, Any]] = None
    ) -> None:
        # Uvicore HTTP module is installed and we are running as HTTP
        if has_http and uvicore.app.is_http:
            # Call uvicores base HTTPException
            if not status_code: status_code = 500
            super().__init__(
                status_code=status_code,
                message=message,  # None message will show defailt HTTP status code phrase
                detail=detail,
                exception=exception,
                extra=extra,
                headers=headers,
            )
        else:
            # Uvicore HTTP module is not installed and/or we are not running as HTTP (from CLI)
            # Status code for CLI is still applicable, can use as bash exit code or general error code instead
            if not status_code: status_code = 1  # Bash catch all for general errors
            if not message: message = 'An error has occured'
            self.status_code = status_code
            self.message = message
            self.detail = detail
            self.exception = exception if uvicore.config.app.debug else None  # Hidden unless in debug mode
            self.extra = extra
            # No need for self.headers in CLI

