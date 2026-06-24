import uvicore
import sqlalchemy as sa
from uvicore.database import Table


@uvicore.table()
class Warehouses(Table):
    """Parent table whose children reference it by a NATURAL key (`code`),
    NOT by its primary key (`id`).  Mirrors the real-world ros.key pattern."""

    name = 'warehouses'
    connection = 'app1'

    schema = [
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('code', sa.String(length=20), unique=True),   # natural key
        sa.Column('name', sa.String(length=100)),
    ]

    schema_kwargs = {
        'sqlite_autoincrement': True,
    }
