from environs import Env

# New environs Env instance
env = Env()

# Public API for import * and doc gens
__all__ = [
    'Env', 'env',
]
