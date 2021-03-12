from abc import ABC, abstractmethod
from uvicore.contracts.user import User


class UserProvider(ABC):

    @abstractmethod
    def retrieve_by_id(self, id) -> User:
        """Retrieve the user from the database by primary key.  No validation."""
        pass

    @abstractmethod
    async def retrieve_by_uuid(self, uuid: str) -> User:
        """Retrieve the user from the database by uuid.  No validation."""
        pass

    @abstractmethod
    async def retrieve_by_username(self, username: str) -> User:
        """Retrieve the user from the database by username.  No validation."""
        pass

    @abstractmethod
    async def retrieve_by_credentials(self, username: str, password: str) -> User:
        """Retrieve the user from the database by username and validate the password"""
        pass

    # @abstractmethod
    # async def validateCredentials(user, password: str) -> bool:
    #     """# Validates an existing user"""
    #     pass


