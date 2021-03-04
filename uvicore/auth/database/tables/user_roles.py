import uvicore
import sqlalchemy as sa
from uvicore.database import Table
from uvicore.support.dumper import dump, dd


# Get related tablenames with proper prefixes
users = uvicore.db.tablename('auth.users')
roles = uvicore.db.tablename('auth.roles')

@uvicore.table()
class UserRoles(Table):

    # Actual database table name
    # Plural table names and singluar model names are encouraged
    # Do not add a package prefix, leave that to the connection config
    name = 'user_roles'

    # Connection for this database from your config file
    connection = 'auth'

    # SQLAlchemy Table definition as a list (exclude name and metadata)
    # This will be converted into an actual SQLAlchemy Table() instance
    # See https://docs.sqlalchemy.org/en/13/core/schema.html
    schema = [
        sa.Column('user_id', sa.Integer, sa.ForeignKey(f"{users}.id"), nullable=False),
        sa.Column('role_id', sa.Integer, sa.ForeignKey(f"{roles}.id"), nullable=False),
        sa.PrimaryKeyConstraint('user_id', 'role_id')
    ]

    # Optional SQLAlchemy Table() instance kwargs
    schema_kwargs = {}
