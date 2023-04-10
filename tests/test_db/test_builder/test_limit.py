import pytest
import uvicore
import sqlalchemy as sa
from uvicore.support.dumper import dump

# DB Builder

@pytest.mark.asyncio
async def test_limit(app1):
    hashtags = (await uvicore.db.query()
        .table('hashtags')
        .limit(2)
        .order_by('id', 'DESC')
        .get()
    )
    dump(hashtags)
    assert [5, 4] == [x.id for x in hashtags]


@pytest.mark.asyncio
async def test_limit_offset(app1):
    hashtags = (await uvicore.db.query()
        .table('hashtags')
        .limit(2)
        .offset(1)
        .order_by('id', 'DESC')
        .get()
    )
    dump(hashtags)
    assert [4, 3] == [x.id for x in hashtags]
