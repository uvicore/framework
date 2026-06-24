import uvicore
import sqlalchemy as sa
from uvicore.database import Table


@uvicore.table()
class Depots(Table):
    """Parent whose natural identity is a COMPOSITE key (region, code).
    `code` alone is NOT unique (it repeats across regions) -- mirrors a sharded
    schema where the shard key (region) must be part of every join."""

    name = 'depots'
    connection = 'app1'

    schema = [
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('region', sa.String(length=20), nullable=False, index=True),
        sa.Column('code', sa.String(length=20), nullable=False, index=True),
        sa.Column('name', sa.String(length=100)),
    ]

    schema_kwargs = {
        'sqlite_autoincrement': True,
    }
