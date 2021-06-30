import uvicore
from uvicore.typing import Any, Dict, Optional, List
from starlette.exceptions import HTTPException as _HTTPException
from uvicore.http import status

# This is how you could do it
#log = lambda : uvicore.log.name('uvicore.http')

class HTTPException(_HTTPException):
    def __init__(self, status_code: int, detail: Any = None, headers: Optional[Dict[str, Any]] = None) -> None:
        # NO, don't want logging for this
        # log().error("HTTPException {} - {}".format(status_code, detail))
        super().__init__(status_code=status_code, detail=detail)
        self.headers = headers


class PermissionDenied(HTTPException):
    def __init__(self, permissions: Optional[List] = None, message: str = None, *, headers: Optional[Dict[str, Any]] = None):
        detail = "Permission denied"
        if permissions:
            if type(permissions) != list: permissions = [permissions]
            detail += " to {}".format(permissions)
        if message: detail += ' - ' + str(message)
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers=headers,
        )


class NotAuthenticated(HTTPException):
    def __init__(self, message: str = None, *, headers: Optional[Dict[str, Any]] = None):
        detail = 'Not authenticated'
        if message: detail += ' - ' + str(message)
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers=headers,
        )


class InvalidCredentials(HTTPException):
    def __init__(self, message: str = None, *, headers: Optional[Dict[str, Any]] = None):
        detail = 'Invalid credentials'
        if message: detail += ' - ' + str(message)
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers=headers,
        )


class NotFound(HTTPException):
    def __init__(self, message: str = None, *, headers: Optional[Dict[str, Any]] = None):
        detail = 'Not found'
        if message: detail += ' - ' + str(message)
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            headers=headers,
        )
