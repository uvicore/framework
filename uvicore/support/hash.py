import hashlib
from typing import Any

def md5(item: Any):
    """Create an md5 hash of the given item"""
    return hashlib.md5(item.encode('utf-8')).hexdigest()
