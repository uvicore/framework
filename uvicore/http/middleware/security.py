import uvicore
from fastapi.params import Depends
from fastapi.params import Security as SecurityBase
from uvicore.typing import Optional, Sequence, Callable, Any, List
from uvicore.support.dumper import dump, dd
from uvicore.support import module

# NOTE, always extend an actual fastapi.params.Security as FastAPI has hard coded values
# to dependency inject that specific class.  You can create and EXTEND one here, but do
# not fully re-create your own.

class Security(SecurityBase):
    """Uvicore Security Depends for FastAPI"""

    # def __init__(self, guard: str = None):
    #     if guard is None: guard = uvicore.config.app.auth.default
    #     self.guard = guard

    def __init__(self, scopes: Optional[Sequence[str]] = None, guard: str = None):
        # # Swap guard and scopes
        # if scopes is None and type(guard) == list:
        #     scopes: Sequence[str] = guard
        #     guard = None

        # Ensure scopes is a List, to allow for singles
        if type(scopes) == str: scopes = [scopes]

        # Do NOT apply a default guard to self.guard, let it be None
        # So I know its blank so I can overwrite it with a parent guard if needed
        self.scopes = scopes
        self.guard = guard

        # Get actual guard from app config
        if guard is None: guard = uvicore.config.app.auth.default
        #guard = guard or self.guard
        if guard not in uvicore.config.app.auth.guards:
            raise Exception('Guard {} not found in app config'.format(guard))
        guard_config = uvicore.config.app.auth.guards[guard]
        provider = uvicore.config.app.auth.providers[guard_config.get('provider')]

        if not guard or not provider:
            raise Exception('Guard {} or provider {} not found'.format(guard, guard_config.get('provider')))

        # Import guard module
        auth = module.load(guard_config.driver).object

        # Call parent Depends
        super().__init__(dependency=auth(guard, provider), scopes=scopes, use_cache=True)

        # Return self
        #return self
