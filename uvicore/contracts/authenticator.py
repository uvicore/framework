from abc import ABC, abstractmethod
from uvicore.contracts.user import User
from uvicore.typing import Optional, Tuple, Dict, List, Union
try:
    from starlette.requests import HTTPConnection
except:
    HTTPConnection = None


class Authenticator(ABC):

    @abstractmethod
    async def authenticate(self, conn: HTTPConnection) -> Union[User, bool]:
        pass

    @abstractmethod
    async def retrieve_user(self, username: str, password: str, provider: Dict) -> Optional[User]:
        pass

    @abstractmethod
    def auth_header(self, request) -> Tuple[str, str, str]:
        pass
