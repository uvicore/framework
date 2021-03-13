from abc import ABC, abstractmethod
from uvicore.contracts.user import User
from uvicore.http.request import HTTPConnection
from uvicore.typing import Optional, Tuple, Dict, List, Union


class Authenticator(ABC):

    @abstractmethod
    async def authenticate(self, conn: HTTPConnection) -> Union[User, bool]:
        pass

    # This can probably not be here and be _
    @abstractmethod
    async def retrieve_user(self, username: str, password: str, provider: Dict) -> Optional[User]:
        pass

    # NO, needs to move
    @abstractmethod
    def validate_permissions(self, user: User, scopes: List) -> None:
        pass

    # This can probably not be here and be _
    @abstractmethod
    def auth_header(self, request) -> Tuple[str, str, str]:
        pass
