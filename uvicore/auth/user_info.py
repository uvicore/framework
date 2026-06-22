import uvicore
from typing import List
from pydantic import BaseModel as PydanticModel
from uvicore.contracts import UserInfo as UserInfoInterface


# Pydantic model because we often return this class in API endpoints
# Endpoints can return classes, but pydantic forces a __initialized__ property
# on them which is annoying.
@uvicore.service()
class UserInfo(PydanticModel, UserInfoInterface):
    """Auth logged in user dataclass representation

    Not to be confused with the User database ORM model.  Logged in Auth User
    requires its own interface and abstraction from any model.  We call it UserInfo.
    """

    # Required even through they are in the contract simply because
    # this is a pydantic model
    id: int
    uuid: str
    username: str
    email: str
    first_name: str
    last_name: str
    # Pydantic v2: Optional[x] requires an explicit default to remain optional.
    title: str | None = None
    avatar: str | None = None
    groups: List[str]
    roles: List[str]
    permissions: List[str]
    superadmin: bool
    authenticated: bool
    extra: dict | None = None

    @property
    def name(self):
        """First and last name"""
        return str(self.first_name + ' ' + self.last_name).strip()

    @property
    def avatar_url(self):
        """Alias to avatar"""
        return self.avatar

    @property
    def admin(self):
        """Check if user is a superadmin"""
        return self.superadmin

    @property
    def is_admin(self):
        """Check if user is a superadmin"""
        return self.superadmin

    @property
    def is_superadmin(self):
        """Check if user is a superadmin"""
        return self.superadmin

    @property
    def is_not_admin(self):
        """Check if user is not a superadmin"""
        return not self.superadmin

    @property
    def is_authenticated(self):
        """Check if user is logged in"""
        return self.authenticated

    @property
    def loggedin(self):
        """Check if user is logged in"""
        return self.authenticated

    @property
    def is_loggedin(self):
        """Check if user is logged in"""
        return self.authenticated

    @property
    def is_not_loggedin(self):
        """Check if user is not logged in"""
        return not self.authenticated

    @property
    def is_not_authenticated(self):
        """Check if user is not logged in"""
        return not self.authenticated

    @property
    def check(self):
        """Alias to authenticated"""
        return self.authenticated

    def can(self, permissions: str | List) -> bool:
        """Check if user has ALL of these permissions"""
        if self.superadmin: return True

        permissions = [permissions] if isinstance(permissions, str) else list(permissions)

        for permission in permissions:
            if permission not in self.permissions:
                return False
        return True

    def can_any(self, permissions: str | List) -> bool:
        """Check if user has any one of these permissions"""
        if self.superadmin: return True

        permissions = [permissions] if isinstance(permissions, str) else list(permissions)

        for permission in permissions:
            if permission in self.permissions:
                return True
        return False

    def cant(self, permissions: str | List) -> bool:
        """Check if user does not have one of these permissions"""
        return not self.can(permissions)

    def cannot(self, permissions: str | List) -> bool:
        """Alias to cant"""
        return self.cant(permissions)
