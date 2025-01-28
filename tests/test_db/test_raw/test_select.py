import pytest
import uvicore
import sqlalchemy as sa
from uvicore.support.dumper import dump


# FIXME, add more tests for .one, .one_or_none, .scalars, .scalar, .scalar_one, .scalar_one_or_none, insertmany, insertone

@pytest.mark.asyncio
async def test_select_all(app1):
    # .all() and .fetchall() are identical
    # Returns empty List of no records found
    results1 = await uvicore.db.all('SELECT * FROM posts')
    results2 = await uvicore.db.fetchall('SELECT * FROM posts')
    results3 = await uvicore.db.all('SELECT * FROM posts WHERE id > 999999')
    results4 = await uvicore.db.fetchall('SELECT * FROM posts WHERE id > 999999')
    assert len(results1) == 7
    assert len(results2) == 7
    assert len(results3) == 0
    assert len(results4) == 0


@pytest.mark.asyncio
async def test_select_first(app1):
    # .first() and .fetchone() are identical
    # Returns empty List of no records found
    results1 = await uvicore.db.first('SELECT * FROM posts ORDER BY id')
    results2 = await uvicore.db.fetchone('SELECT * FROM posts ORDER BY id')
    results3 = await uvicore.db.first('SELECT * FROM posts WHERE id = 999999')
    results4 = await uvicore.db.fetchone('SELECT * FROM posts WHERE id = 999999')
    assert results1.id == 1
    assert results2.id == 1
    assert results3 is None
    assert results4 is None
