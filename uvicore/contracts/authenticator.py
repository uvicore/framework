from abc import ABC, abstractmethod
from uvicore.contracts.user_info import UserInfo
from uvicore.typing import Optional, Tuple, Dict, List, Union
try:
    from starlette.requests import HTTPConnection
except ImportError:  # pragma: nocover
    HTTPConnection = None  # type: ignore


class Authenticator(ABC):

    @abstractmethod
    async def authenticate(self, conn: HTTPConnection) -> Union[UserInfo, bool]:
        pass

    @abstractmethod
    async def retrieve_user(self, username: str, password: str, provider: Dict) -> Optional[UserInfo]:
        """Retrieve user from User Provider backend"""
        pass

    @abstractmethod
    async def create_user(self, provider: Dict, request: HTTPConnection, **kwargs):
        """Create new user in backend"""
        pass

    @abstractmethod
    async def sync_user(self, provider: Dict, request: HTTPConnection, **kwargs):
        """Sync user and group linkage to backend"""
        pass

    @abstractmethod
    def auth_header(self, request) -> Tuple[str, str, str]:
        """Extract authorization header parts"""
        pass
