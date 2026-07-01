import uvicore
from app1.models.depot import Depot
from app1.models.slot import Slot
from uvicore import log


@uvicore.seeder()
async def seed():
    log.item('Seeding table depots')

    # Same `code` ('D1') exists in TWO regions on purpose.  A single-key join on
    # code alone would wrongly cross-match both depots; only the composite
    # (region, code) join keeps them separate.
    await Depot.insert([
        {'region': 'US', 'code': 'D1', 'name': 'US-D1'},
        {'region': 'EU', 'code': 'D1', 'name': 'EU-D1'},
    ])

    await Slot.insert([
        {'region': 'US', 'depot_code': 'D1', 'label': 'US-S1'},
        {'region': 'US', 'depot_code': 'D1', 'label': 'US-S2'},
        {'region': 'EU', 'depot_code': 'D1', 'label': 'EU-S1'},
    ])
