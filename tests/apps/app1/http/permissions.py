import uvicore
from uvicore.typing import List
from uvicore.contracts import User
from uvicore.support.dumper import dump, dd


@uvicore.service()
class Mapper:
    """Static stateless role to permission mappings"""

    mapping = {
        'Anonymous': [
            'anonymous',
            'posts.read',
        ],
        'Employee': [
            'posts.read',
        ],
    }

    async def __call__(self, user: User) -> List:
        permissions = []
        for role in user.roles:
            if role in self.mapping:
                permissions.extend(self.mapping[role])
        return permissions



