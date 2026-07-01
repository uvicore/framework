import uvicore
import sqlalchemy as sa
from uvicore.database import Table


@uvicore.table()
class Bins(Table):
    """Child of warehouses linked by warehouse_code -> warehouses.code (a
    non-primary-key natural key).  No ForeignKey constraint on purpose, the
    link is purely a natural key like the production schema."""

    name = 'bins'
    connection = 'app1'

    schema = [
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('warehouse_code', sa.String(length=20), nullable=False, index=True),
        sa.Column('label', sa.String(length=100)),
    ]

    schema_kwargs = {
        'sqlite_autoincrement': True,
    }
