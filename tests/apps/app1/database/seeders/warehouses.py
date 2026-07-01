import uvicore
from app1.models.warehouse import Warehouse
from app1.models.bin import Bin
from app1.models.warehouse_meta import WarehouseMeta
from uvicore import log


@uvicore.seeder()
async def seed():
    log.item('Seeding table warehouses')

    # Parents (note: ids auto-increment 1, 2 -- but children link by `code`)
    await Warehouse.insert([
        {'code': 'WH-A', 'name': 'Alpha'},
        {'code': 'WH-B', 'name': 'Beta'},
    ])

    # Children linked by the NATURAL key warehouse_code (NOT the parent id)
    await Bin.insert([
        {'warehouse_code': 'WH-A', 'label': 'A1'},
        {'warehouse_code': 'WH-A', 'label': 'A2'},
        {'warehouse_code': 'WH-B', 'label': 'B1'},
    ])

    # One-to-one meta linked by the natural key
    await WarehouseMeta.insert([
        {'warehouse_code': 'WH-A', 'note': 'meta for alpha'},
        {'warehouse_code': 'WH-B', 'note': 'meta for beta'},
    ])
