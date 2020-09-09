import pytest
from uvicore.support import hash as h

def test_md5():
    x = h.md5('Uvicore is amazing')
    assert x == '32b7d455a16d63558557b3cf10ff0da0'
