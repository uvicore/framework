import pytest
from uvicore.support import path


def test_find_base():
    # Test successful path find
    assumed = __file__.replace('/tests/test_unit/test_support/test_path.py', '')
    base = path.find_base(__file__)
    assert base == assumed

    # Test failed path find (which calls exit())
    with pytest.raises(SystemExit):
        path.find_base('/')
