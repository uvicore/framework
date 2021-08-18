from uvicore.typing import Any, Dict, Optional
has_http = True
try:
    from starlette.exceptions import HTTPException as BaseException
except:
    BaseException = Exception
    has_http = False

class SmartException(BaseException):
    def __init__(self, status_code: int, detail: Any = None, headers: Optional[Dict[str, Any]] = None) -> None:
        if has_http:
            super().__init__(status_code=status_code, detail=detail)
            self.headers = headers
        else:
            self.status_code = status_code
            self.detail = detail
