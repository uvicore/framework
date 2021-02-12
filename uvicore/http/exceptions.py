from typing import Any, Dict, Optional, Sequence
from starlette.exceptions import HTTPException as _HTTPException


class HTTPException(_HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail)
        self.headers = headers
