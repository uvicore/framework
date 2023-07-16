import hashlib
from typing import Any

def md5(item: Any):
    """Create an md5 hash of the given item"""
    return hashlib.md5((str(item)).encode('utf-8')).hexdigest()

def sha1(item: Any):
    return hashlib.sha1((str(item)).encode('utf-8')).hexdigest()

def sha256(item: Any):
    return hashlib.sha256((str(item)).encode('utf-8')).hexdigest()

def sha512(item: Any):
    return hashlib.sha512((str(item)).encode('utf-8')).hexdigest()
