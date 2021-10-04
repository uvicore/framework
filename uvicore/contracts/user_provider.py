from abc import ABC, abstractmethod
from uvicore.typing import Union, List, Dict
from uvicore.contracts.user_info import UserInfo
try:
    from starlette.requests import HTTPConnection
except:
    HTTPConnection = None


class UserProvider(ABC):

    def __init__(self):
        # Default field mapping for each method below, easily overridable in your custom user providers!
        self.field_map = {
            'id': 'id',
            'uuid': 'uuid',
            'username': 'username',
        }

    async def retrieve_by_id(self, id: Union[str, int], request: HTTPConnection, **kwargs) -> UserInfo:
        """Retrieve user by primary key from the user provider backend.  No validation."""
        field = self.field_map['id']
        return await self._retrieve_user(field, id, request, **kwargs)

    async def retrieve_by_uuid(self, uuid: str, request: HTTPConnection, **kwargs) -> UserInfo:
        """Retrieve the user by uuid from the user provider backend.  No validation."""
        field = self.field_map['uuid']
        return await self._retrieve_user(field, uuid, request, **kwargs)

    async def retrieve_by_username(self, username: str, request: HTTPConnection, **kwargs) -> UserInfo:
        """Retrieve the user by username from the user provider backend.  No validation."""
        field = self.field_map['username']
        return await self._retrieve_user(field, username, request, **kwargs)

    async def retrieve_by_credentials(self, username: str, password: str, request: HTTPConnection, **kwargs) -> UserInfo:
        """Retrieve the user by username from the user provider backend AND validate the password if not None"""
        field = self.field_map['username']
        return await self._retrieve_user(field, username, request, password=password, **kwargs)

    @abstractmethod
    async def create_user(self, request: HTTPConnection, **kwargs):
        """Create new user in backend"""

    @abstractmethod
    async def sync_user(self, request: HTTPConnection, **kwargs):
        """Sync user to backend"""

    # @abstractmethod
    # async def retrieve_by_id(self, id: Union[str, int], request: HTTPConnection, options: Dict = {}) -> UserInfo:
    #     """Retrieve user by primary key from the user provider backend.  No validation."""

    # @abstractmethod
    # async def retrieve_by_uuid(self, uuid: str, request: HTTPConnection, options: Dict = {}) -> UserInfo:
    #     """Retrieve the user by uuid from the user provider backend.  No validation."""

    # @abstractmethod
    # async def retrieve_by_username(self, username: str, request: HTTPConnection, options: Dict = {}) -> UserInfo:
    #     """Retrieve the user by username from the user provider backend.  No validation."""

    # @abstractmethod
    # async def retrieve_by_credentials(self, username: str, password: str, request: HTTPConnection, options: Dict = {}) -> UserInfo:
    #     """Retrieve the user by username from the user provider backend AND validate the password if not None"""
