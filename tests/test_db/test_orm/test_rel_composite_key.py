"""Composite (multi-column) JOIN ON conditions for relations.

A relation may declare ordered lists for foreign_key/local_key so the JOIN ON
clause spans multiple columns (e.g. a shard key + a natural key), ANDed in the
declared order:

    HasMany('app1.models.slot.Slot',
            foreign_key=['region', 'depot_code'],
            local_key =['region', 'code'])

Required for sharded backends (Vitess/PlanetScale) that must include the shard
key in every join.  The seed data deliberately reuses code 'D1' across the 'US'
and 'EU' regions so that a single-column join would cross-match -- only the
composite (region, code) join keeps them separate.
"""
import pytest
import uvicore
from uvicore.support.dumper import dump, dd


@pytest.mark.asyncio
async def test_composite_has_many(app1):
    from app1.models.depot import Depot
    from app1.models.slot import Slot  # coverage

    depots = await Depot.query().include('slots').get()
    slots_by_name = {d.name: sorted([s.label for s in d.slots]) for d in depots}
    assert slots_by_name == {
        'US-D1': ['US-S1', 'US-S2'],
        'EU-D1': ['EU-S1'],
    }


@pytest.mark.asyncio
async def test_composite_does_not_cross_match(app1):
    from app1.models.depot import Depot

    # The US depot must NOT pick up the EU slot even though both share code 'D1'
    depots = await Depot.query().include('slots').where('region', 'US').get()
    assert len(depots) == 1
    labels = sorted([s.label for s in depots[0].slots])
    assert labels == ['US-S1', 'US-S2']
    assert 'EU-S1' not in labels


@pytest.mark.asyncio
async def test_composite_belongs_to_inverse(app1):
    from app1.models.slot import Slot

    slots = await Slot.query().include('depot').order_by('id').get()
    assert [(s.label, s.depot.name) for s in slots] == [
        ('US-S1', 'US-D1'),
        ('US-S2', 'US-D1'),
        ('EU-S1', 'EU-D1'),
    ]


@pytest.mark.asyncio
async def test_composite_has_many_with_limit(app1):
    from app1.models.depot import Depot

    # LIMIT counts parents; the limited parent still gets all composite-matched children
    depots = await Depot.query().include('slots').limit(1).get()
    assert len(depots) == 1
    assert depots[0].name == 'US-D1'
    assert ['US-S1', 'US-S2'] == sorted([s.label for s in depots[0].slots])


@pytest.mark.asyncio
async def test_composite_join_on_clause_order(app1):
    from app1.models.depot import Depot

    # The generated JOIN ON must AND both conditions, in the DECLARED order
    # (region pair first, then code/depot_code pair).
    sql = Depot.query().include('slots').sql()
    slots_sql = sql['slots']
    on = slots_sql[slots_sql.find(' ON '):]
    where_at = on.find(' WHERE ')
    if where_at != -1:
        on = on[:where_at]
    assert ' AND ' in on                          # two conditions joined
    assert on.index('region') < on.index('depot_code')   # region pair declared first
