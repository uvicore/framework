import uvicore
from uvicore.typing import Any, Dict, Optional, List
from starlette.exceptions import HTTPException as _HTTPException
from uvicore.http import status

# This is how you could do it, if you wanted to log
#log = lambda : uvicore.log.name('uvicore.http')

# See https://www.restapitutorial.com/httpstatuscodes.html for a good list to follow

class HTTPException(_HTTPException):
    """Main Base HTTP Exception"""

    # Message is optional and will default the the HTTP status codes TEXT as outlined in the python http module
    # Detail is a more detailed text description of the issue
    # Extra lets you pass in a dict of options or extra information that some handlers may want to use
    def __init__(self,
        status_code: int,
        detail: Optional[str] = None,
        *,
        message: Optional[str] = None,
        exception: Optional[str] = None,
        extra: Optional[Dict] = None,
        headers: Optional[Dict[str, Any]] = None
    ) -> None:
        # Call starlette exception where their detail is my message
        super().__init__(status_code=status_code, detail=message)

        # Swap starlette detail to my message
        self.message = self.detail
        self.detail = detail
        self.exception = exception if uvicore.config.app.debug else None  # Hidden unless in debug mode
        self.extra = extra
        self.headers = headers


class PermissionDenied(HTTPException):
    """Permission Denied Exception"""
    def __init__(self,
        permissions: Optional[List] = None,
        detail: Optional[str] = None,
        *,
        extra: Optional[Dict] = None,
        headers: Optional[Dict[str, Any]] = None
    ) -> None:
        detail = "Permission denied"
        if permissions:
            if type(permissions) != list: permissions = [permissions]
            detail += " to {}".format(permissions)
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message='Permission Denied',
            detail=detail,
            extra=extra,
            headers=headers,
        )


class NotAuthenticated(HTTPException):
    """Not Authenticated Exception"""
    def __init__(self,
        detail: Optional[str] = None,
        *,
        extra: Optional[Dict] = None,
        headers: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message='Not Authenticated',
            detail=detail,
            extra=extra,
            headers=headers,
        )


class InvalidCredentials(HTTPException):
    """Invalid Credentials Exception"""
    def __init__(self,
        detail: Optional[str] = None,
        *,
        extra: Optional[Dict] = None,
        headers: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message='Invalid Credentials',
            detail=detail,
            extra=extra,
            headers=headers,
        )


class NotFound(HTTPException):
    """Not Found Exception"""
    def __init__(self,
        detail: Optional[str] = None,
        *,
        extra: Optional[Dict] = None,
        headers: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message='Not Found',
            detail=detail,
            extra=extra,
            headers=headers,
        )


class BadParameter(HTTPException):
    """Bad Parameter"""
    def __init__(self,
        detail: Optional[str] = None,
        *,
        exception: Optional[str] = None,
        extra: Optional[Dict] = None,
        headers: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            message='Bad Parameter',
            detail=detail,
            exception=exception,
            extra=extra,
            headers=headers,
        )
