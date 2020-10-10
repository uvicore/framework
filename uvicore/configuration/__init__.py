from environs import Env


# The configuration package uses a __init__.py because users will import these
# methods from their own configs and we want a nicer import which looks
# like - from uvicore.configuration import env

# New environs Env instance
env = Env()

# Public API for import * and doc gens
__all__ = [
    'Env', 'env',
]
