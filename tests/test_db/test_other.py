import pytest
import uvicore
import sqlalchemy as sa
from uvicore.support.dumper import dump

# DB Other - For 100% code coverage
# All misc items missed from the other test_* folders

@pytest.mark.asyncio
async def test_db_get_packages_by_connection(app1):

    packages = uvicore.db.packages('app1')
    dump(packages)
    assert len(packages) == 2
    assert packages[0].name == 'uvicore.auth'
    assert packages[1].name == 'app1'


@pytest.mark.asyncio
async def test_db_get_tables(app1):
    tables = uvicore.db.tables()
    assert tables is not None


@pytest.mark.asyncio
async def test_db_get_invalid_metakey(app1):
    # Exception defined in db/db.py metakey()
    with pytest.raises(Exception) as e:
        metakey = uvicore.db.metakey('invalid_connection')

    assert 'Metakey not found' in str(e)
