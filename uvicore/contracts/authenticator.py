from abc import ABC, abstractmethod
from uvicore.contracts.user import User
from uvicore.http.request import HTTPConnection
from uvicore.typing import Optional, Tuple, Dict, List


class Authenticator(ABC):

    @abstractmethod
    async def authenticate(self, conn: HTTPConnection) -> Optional[User]:
        pass

    @abstractmethod
    async def retrieve_user(self, username: str, password: str, provider: Dict) -> Optional[User]:
        pass

    @abstractmethod
    def validate_permissions(self, user: User, scopes: List) -> None:
        pass

    @abstractmethod
    def auth_header(self, request) -> Tuple[str, str, str]:
        pass
