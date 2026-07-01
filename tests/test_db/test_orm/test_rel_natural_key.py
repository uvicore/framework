"""Eager-loading *Many/*One relations whose local_key is a NATURAL key
(NOT the parent's primary key), e.g. warehouses.code = bins.warehouse_code.

Regression coverage for the bug where HasMany/HasOne children failed to
attach because the in-memory merge indexed parents by their primary key
instead of by the relation's local_key.
"""
import pytest
import uvicore
from uvicore.support.dumper import dump, dd


@pytest.mark.asyncio
async def test_has_many_natural_key(app1):
    from app1.models.warehouse import Warehouse
    from app1.models.bin import Bin  # for coverage

    # One Warehouse (pk id=1, code 'WH-A') has Many Bins linked by code
    warehouse = await Warehouse.query().include('bins').find(1)
    assert warehouse.code == 'WH-A'
    assert warehouse.bins is not None
    assert ['A1', 'A2'] == sorted([b.label for b in warehouse.bins])


@pytest.mark.asyncio
async def test_has_many_natural_key_multiple_parents(app1):
    from app1.models.warehouse import Warehouse

    # Eager-load bins across ALL warehouses at once (exercises parent matching
    # across multiple parents keyed by their natural code, not their id)
    warehouses = await Warehouse.query().include('bins').get()
    bins_by_code = {w.code: sorted([b.label for b in w.bins]) for w in warehouses}
    assert bins_by_code == {
        'WH-A': ['A1', 'A2'],
        'WH-B': ['B1'],
    }


@pytest.mark.asyncio
async def test_has_one_natural_key(app1):
    from app1.models.warehouse import Warehouse

    # One Warehouse has One meta record linked by the natural code key
    warehouse = await Warehouse.query().include('meta').find(1)
    assert warehouse.meta is not None
    assert warehouse.meta.note == 'meta for alpha'


@pytest.mark.asyncio
async def test_has_many_natural_key_with_limit(app1):
    from app1.models.warehouse import Warehouse

    # LIMIT must count PARENT rows, not the joined child rows.  Before the fix
    # this returned a single warehouse with NO bins (the *Many join multiplied
    # rows and LIMIT truncated to one child row).
    warehouses = await Warehouse.query().include('bins').limit(1).get()
    assert len(warehouses) == 1
    assert warehouses[0].code == 'WH-A'
    # And the limited parent must still get ALL its children attached
    assert ['A1', 'A2'] == sorted([b.label for b in warehouses[0].bins])


@pytest.mark.asyncio
async def test_belongs_to_natural_key_inverse(app1):
    from app1.models.bin import Bin

    # Inverse: each Bin BelongsTo one Warehouse via warehouse_code = code
    bins = await Bin.query().include('warehouse').order_by('id').get()
    assert [b.warehouse.code for b in bins] == ['WH-A', 'WH-A', 'WH-B']
    assert [b.warehouse.name for b in bins] == ['Alpha', 'Alpha', 'Beta']
