import pytest
import uvicore
import sqlalchemy as sa
from uvicore.support.dumper import dump

# DB Builder

@pytest.mark.asyncio
async def test_missing_table(app1):
    # Exception defined in db/query.py table()
    with pytest.raises(Exception) as e:
        x = (await uvicore.db.query().table('x').get())

    assert 'Table x not found' in str(e)
