import uvicore
import sqlalchemy as sa
from uvicore.database import Table


@uvicore.table()
class Slots(Table):
    """Child of depots linked by the COMPOSITE key (region, depot_code) ->
    depots (region, code)."""

    name = 'slots'
    connection = 'app1'

    schema = [
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('region', sa.String(length=20), nullable=False, index=True),
        sa.Column('depot_code', sa.String(length=20), nullable=False, index=True),
        sa.Column('label', sa.String(length=100)),
    ]

    schema_kwargs = {
        'sqlite_autoincrement': True,
    }
