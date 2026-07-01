import uvicore
import sqlalchemy as sa
from uvicore.database import Table


@uvicore.table()
class WarehouseMeta(Table):
    """One-to-one child of warehouses linked by warehouse_code ->
    warehouses.code (non-primary-key natural key).  Exercises HasOne on a
    natural key."""

    name = 'warehouse_meta'
    connection = 'app1'

    schema = [
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('warehouse_code', sa.String(length=20), unique=True),
        sa.Column('note', sa.String(length=255)),
    ]

    schema_kwargs = {
        'sqlite_autoincrement': True,
    }
