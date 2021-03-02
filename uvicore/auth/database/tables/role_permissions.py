import uvicore
import sqlalchemy as sa
from uvicore.database import Table
from uvicore.support.dumper import dump, dd


# Get related tablenames with proper prefixes
roles = uvicore.db.tablename('auth.roles')
permissions = uvicore.db.tablename('auth.permissions')

@uvicore.table()
class RolePermissions(Table):

    # Actual database table name
    # Plural table names and singluar model names are encouraged
    # Do not add a package prefix, leave that to the connection config
    name = 'role_permissions'

    # Connection for this database from your config file
    connection = 'auth'

    # SQLAlchemy Table definition as a list (exclude name and metadata)
    # This will be converted into an actual SQLAlchemy Table() instance
    # See https://docs.sqlalchemy.org/en/13/core/schema.html
    schema = [
        sa.Column('role_id', sa.Integer, sa.ForeignKey(f"{roles}.id"), nullable=False),
        sa.Column('permission_id', sa.Integer, sa.ForeignKey(f"{permissions}.id"), nullable=False),
        sa.PrimaryKeyConstraint('role_id', 'permission_id')
    ]

    # Optional SQLAlchemy Table() instance kwargs
    schema_kwargs = {}
