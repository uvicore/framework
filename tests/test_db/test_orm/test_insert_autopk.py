"""
Regression test for portable auto-increment primary keys.

The ORM mapper used to include a model's primary key in the INSERT column dict
even when its value was None. SQLite tolerates an explicit NULL on an INTEGER
PRIMARY KEY (autoincrements), but Postgres/MySQL reject NULL on a serial/identity
PK -> "null value in column \"id\" violates not-null constraint". The mapper now
omits a None-valued primary key so the database generates it on every dialect.

Permission.id is `primary=True` but NOT `read_only=True`, so it is the perfect
case to lock in (a model that did not opt into read_only on its PK).
"""
import pytest


@pytest.mark.asyncio
async def test_table_mapper_omits_none_primary_key(app1):
    from uvicore.auth.models.permission import Permission
    row = Permission(name='zzz-autopk-probe', entity=None).mapper().table()
    assert 'id' not in row          # None PK omitted -> DB will auto-generate it
    assert row['name'] == 'zzz-autopk-probe'


@pytest.mark.asyncio
async def test_table_mapper_keeps_provided_primary_key(app1):
    from uvicore.auth.models.permission import Permission
    row = Permission(id=999, name='zzz-autopk-explicit', entity=None).mapper().table()
    assert row['id'] == 999          # an explicitly-set PK is preserved


@pytest.mark.asyncio
async def test_insert_generates_primary_key(app1):
    from uvicore.auth.models.permission import Permission
    await Permission.insert([{'name': 'zzz-autopk-insert', 'entity': None}])
    created = await Permission.query().where('name', 'zzz-autopk-insert').get()
    try:
        assert len(created) == 1
        assert created[0].id is not None and created[0].id > 0
    finally:
        for p in created:
            await p.delete()
