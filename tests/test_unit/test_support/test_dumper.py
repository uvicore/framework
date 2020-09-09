import pytest
from uvicore.support import dumper


def test_dump():
    dumper.dump('hi')


def test_dd():
    with pytest.raises(SystemExit):
        dumper.dd('hi')
