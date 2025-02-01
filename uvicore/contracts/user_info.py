from __future__ import annotations
from dataclasses import dataclass
from abc import ABC, abstractmethod
from uvicore.typing import List, Union

# Why a dataclass instead of a SuperDict?
# Because a dataclass FORCES you to instantiate with ALL these attributes
# making them required.  If one extends the UserInfo all of these are guarenteed
# required in order to instantiate.  This is inherently a good contract.


@dataclass
class UserInfo(ABC):
    """Auth Logged in User Definition"""

    # These class level properties for for type annotations only.
    # They do not restrict of define valid properties like a dataclass would.
    # This is still a fully dynamic SuperDict!
    id: int
    uuid: str
    sub: str
    username: str
    email: str
    first_name: str
    last_name: str
    title: str
    avatar: str
    groups: List[str]
    roles: List[str]
    permissions: List[str]
    superadmin: bool
    authenticated: bool

    @property
    @abstractmethod
    def name(self):
        """First and last name"""

    @property
    @abstractmethod
    def avatar_url(self):
        """Alias to avatar"""

    @property
    @abstractmethod
    def admin(self):
        """Alias to superadmin"""

    @property
    @abstractmethod
    def is_admin(self):
        """Alias to superadmin"""

    @property
    @abstractmethod
    def is_superadmin(self):
        """Alias to superadmin"""

    @property
    @abstractmethod
    def is_authenticated(self):
        """Alias to authenticated"""

    @property
    @abstractmethod
    def loggedin(self):
        """Alias to authenticated"""

    @property
    @abstractmethod
    def is_loggedin(self):
        """Alias to authenticated"""

    @property
    @abstractmethod
    def check(self):
        """Alias to authenticated"""

    def can(self, permissions: Union[str, List]) -> bool:
        """Check if user has ALL of these permissions"""

    def can_any(self, permissions: Union[str, List]) -> bool:
        """Check if user has any one of these permissions"""

    def cant(self, permissions: Union[str, List]) -> bool:
        """Check if user does not have one of these permissions"""

    def cannot(self, permissions: Union[str, List]) -> bool:
        """Alias to cant"""

