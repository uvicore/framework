import uvicore
from uvicore.typing import List, Union
from uvicore.contracts import User as UserInterface
#from uvicore.contracts import UserProvider
from uvicore.support.dumper import dump, dd
#from uvicore.support.hash import sha1
#from uvicore.auth.support import password as pwd


@uvicore.service()
class User(UserInterface):
    """Auth logged in user dataclass representation

    Not to be confused with the User database ORM model.  Logged in Auth User
    requires its own interface and abstraction from any model.
    """

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

    def can(self, permissions: Union[str, List]) -> bool:
        """Check if user has ALL of these permissions"""
        if self.superadmin: return True

        permissions = [permissions] if isinstance(permissions, str) else list(permissions)

        for permission in permissions:
            if permission not in self.permissions:
                return False
        return True

    def can_any(self, permissions: Union[str, List]) -> bool:
        """Check if user has any one of these permissions"""
        if self.superadmin: return True

        permissions = [permissions] if isinstance(permissions, str) else list(permissions)

        for permission in permissions:
            if permission in self.permissions:
                return True
        return False

    def cant(self, permissions: Union[str, List]) -> bool:
        """Check if user does not have one of these permissions"""
        return not self.can(permissions)

    def cannot(self, permissions: Union[str, List]) -> bool:
        """Alias to cant"""
        return self.cant(permissions)



