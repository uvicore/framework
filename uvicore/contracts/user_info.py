from __future__ import annotations
from dataclasses import dataclass
from abc import ABC, abstractmethod
from uvicore.typing import List, Union, Optional

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
    username: str
    email: str
    first_name: str
    last_name: str
    title: Optional[str]
    avatar: Optional[str]
    groups: List[str]
    roles: List[str]
    permissions: List[str]
    superadmin: bool
    authenticated: bool
    extra: Optional[dict]

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
        """Check if user is a superadmin"""

    @property
    @abstractmethod
    def is_admin(self):
        """Check if user is a superadmin"""

    @property
    @abstractmethod
    def is_superadmin(self):
        """Check if user is a superadmin"""

    @property
    @abstractmethod
    def is_not_admin(self):
        """Check if user is not a superadmin"""

    @property
    @abstractmethod
    def is_authenticated(self):
        """Check if user is logged in"""

    @property
    @abstractmethod
    def loggedin(self):
        """Check if user is logged in"""

    @property
    @abstractmethod
    def is_loggedin(self):
        """Check if user is logged in"""

    @property
    @abstractmethod
    def is_not_loggedin(self):
        """Check if user is not logged in"""

    @property
    @abstractmethod
    def is_not_authenticated(self):
        """Check if user is not logged in"""

    @property
    @abstractmethod
    def check(self):
        """Check if user is logged in"""

    def can(self, permissions: Union[str, List]) -> bool:
        """Check if user has ALL of these permissions"""

    def can_any(self, permissions: Union[str, List]) -> bool:
        """Check if user has any one of these permissions"""

    def cant(self, permissions: Union[str, List]) -> bool:
        """Check if user does not have one of these permissions"""

    def cannot(self, permissions: Union[str, List]) -> bool:
        """Alias to cant"""
