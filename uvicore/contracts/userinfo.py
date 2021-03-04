from uvicore.typing import Dict, List
from prettyprinter import pretty_call, register_pretty


class UserInfo(Dict):
    """Auth UserInfo Definition"""

    # These class level properties for for type annotations only.
    # They do not restrict of define valid properties like a dataclass would.
    # This is still a fully dynamic SuperDict!
    id: int
    uuid: str
    email: str
    first_name: str
    last_name: str
    title: str
    avatar_url: str
    groups: List[str]
    roles: List[str]
    permissions: List[str]
    superadmin: bool


@register_pretty(UserInfo)
def pretty_entity(value, ctx):
    """Custom pretty printer for my SuperDict"""
    # This printer removes the class name uvicore.types.Dict and makes it print
    # with a regular {.  This really cleans up the output!

    # SuperDict are printed as Dict, but this Package SuperDict should
    # be printed more like a class with key=value notation, so use **values
    return pretty_call(ctx, 'UserInfo', **value)
