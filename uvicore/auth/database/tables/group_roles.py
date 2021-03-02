import uvicore
import sqlalchemy as sa
from uvicore.database import Table
from uvicore.support.dumper import dump, dd


# Get related tablenames with proper prefixes
groups = uvicore.db.tablename('auth.groups')
roles = uvicore.db.tablename('auth.roles')

@uvicore.table()
class GroupRoles(Table):

    # Actual database table name
    # Plural table names and singluar model names are encouraged
    # Do not add a package prefix, leave that to the connection config
    name = 'group_roles'

    # Connection for this database from your config file
    connection = 'auth'

    # SQLAlchemy Table definition as a list (exclude name and metadata)
    # This will be converted into an actual SQLAlchemy Table() instance
    # See https://docs.sqlalchemy.org/en/13/core/schema.html
    schema = [
        sa.Column('group_id', sa.Integer, sa.ForeignKey(f"{groups}.id"), nullable=False),
        sa.Column('role_id', sa.Integer, sa.ForeignKey(f"{roles}.id"), nullable=False),
        sa.PrimaryKeyConstraint('group_id', 'role_id')
    ]

    # Optional SQLAlchemy Table() instance kwargs
    schema_kwargs = {}
