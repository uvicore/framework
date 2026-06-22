from abc import ABC, abstractmethod
from uvicore.contracts.user_info import UserInfo
from typing import Tuple
from uvicore.typing import Dict

try:
    from starlette.requests import HTTPConnection
except ImportError:
    class HTTPConnection: pass


class Authenticator(ABC):

    @abstractmethod
    async def authenticate(self, conn: HTTPConnection) -> UserInfo | bool:
        pass

    @abstractmethod
    async def retrieve_user(self, username: str, password: str, provider: Dict) -> UserInfo | None:
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
