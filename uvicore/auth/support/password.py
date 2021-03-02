import uvicore
from argon2 import Type
from uvicore.typing import Dict
from argon2 import PasswordHasher
from uvicore.support.dumper import dump, dd
from argon2.exceptions import VerifyMismatchError


def create(password: str, *, type: str = None, hash_len: int = None, salt_len: int = None, encoding: str = None, time_cost: int = None, memory_cost: int = None, parallelism: int = None):
    """Create a new hashed password using config driven Argon2 default or parameter overrides"""
    config = uvicore.config('uvicore.auth.hasher')
    if type is None: type = config.type
    if hash_len is None: hash_len = config.hash_len
    if salt_len is None: salt_len = config.salt_len
    if encoding is None: encoding = config.encoding
    if time_cost is None: time_cost = config.time_cost
    if memory_cost is None: memory_cost = config.memory_cost
    if parallelism is None: parallelism = config.parallelism

    # New Argon2 Password Hasher
    ph = PasswordHasher(type=Type[type], hash_len=hash_len, salt_len=salt_len, encoding=encoding, time_cost=time_cost, memory_cost=memory_cost, parallelism=parallelism)
    return ph.hash(password)

def verify(password: str, hash: str) -> bool:
    if password is None or hash is None: return False
    ph = PasswordHasher()
    verified = False
    try:
        verified = ph.verify(hash, password)
    except VerifyMismatchError:
        pass
    return verified
