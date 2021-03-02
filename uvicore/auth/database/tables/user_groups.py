import uvicore
import sqlalchemy as sa
from uvicore.database import Table
from uvicore.support.dumper import dump, dd


# Get related tablenames with proper prefixes
users = uvicore.db.tablename('auth.users')
groups = uvicore.db.tablename('auth.groups')

@uvicore.table()
class UserGroups(Table):

    # Actual database table name
    # Plural table names and singluar model names are encouraged
    # Do not add a package prefix, leave that to the connection config
    name = 'user_groups'

    # Connection for this database from your config file
    connection = 'auth'

    # SQLAlchemy Table definition as a list (exclude name and metadata)
    # This will be converted into an actual SQLAlchemy Table() instance
    # See https://docs.sqlalchemy.org/en/13/core/schema.html
    schema = [
        sa.Column('user_id', sa.Integer, sa.ForeignKey(f"{users}.id"), nullable=False),
        #sa.Column('group_key', sa.String(length=20), sa.ForeignKey(f"{groups}.key"), nullable=False),
        sa.Column('group_id', sa.Integer, sa.ForeignKey(f"{groups}.id"), nullable=False),
        sa.PrimaryKeyConstraint('user_id', 'group_id')
    ]

    # Optional SQLAlchemy Table() instance kwargs
    schema_kwargs = {}
