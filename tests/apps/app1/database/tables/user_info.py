import sqlalchemy as sa

import uvicore
from uvicore.database import Table
from uvicore.support.dumper import dd, dump

# Get related tablenames with proper prefixes
users = uvicore.db.tablename('auth.users')


@uvicore.table()
class UserInfo(Table):

    # Actual database table name
    # Plural table names and singluar model names are encouraged
    # Do not add a package prefix, leave that to the connection config
    name = 'user_info'

    # Connection for this database from your config file
    connection = 'auth'

    # SQLAlchemy Table definition as a list (exclude name and metadata)
    # This will be converted into an actual SQLAlchemy Table() instance
    # See https://docs.sqlalchemy.org/en/13/core/schema.html
    schema = [
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("extra1", sa.String(length=50)),
        sa.Column('user_id', sa.Integer, sa.ForeignKey(f"{users}.id"), nullable=False),
    ]

    # Optional SQLAlchemy Table() instance kwargs
    schema_kwargs = {}


# IoC Class Instance
#UserInfo: _UserInfo = uvicore.ioc.make('uvicore.auth.database.tables.user_info.UserInfo', _UserInfo, singleton=True)
