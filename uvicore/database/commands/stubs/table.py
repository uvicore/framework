import uvicore
import sqlalchemy as sa
from uvicore.database import Table
from uvicore.support.dumper import dump, dd

# Get related tablenames with proper prefixes
users = uvicore.db.tablename('auth.users')
formats = uvicore.db.tablename('xx_appname.formats')


@uvicore.table()
class xx_TableName(Table):

    # Actual database table name
    # Plural table names and singluar model names are encouraged
    # Do not add a package prefix, leave that to the connection config
    name = 'xx_tablename'

    # Connection for this database from your config file
    connection = 'xx_appname'

    # SQLAlchemy Table definition as a list (exclude name and metadata)
    # This will be converted into an actual SQLAlchemy Table() instance
    # See https://docs.sqlalchemy.org/en/13/core/schema.html
    schema = [
        # Defaults: nullable=False, index=False, unique=False, primary_key=False

        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('slug', sa.String(length=100), unique=True),
        sa.Column('title', sa.String(length=100)),
        sa.Column('body', sa.Text()),
        sa.Column('format', sa.Integer, sa.ForeignKey(f"{formats}.id"), nullable=False),
        sa.Column('view_count', sa.Integer),
        sa.Column('is_deleted', sa.Boolean(), default=False),
        sa.Column('is_hidden', sa.Boolean(), default=False),
        sa.Column('creator_id', sa.Integer, sa.ForeignKey(f"{users}.id"), nullable=False),
        sa.Column('updator_id', sa.Integer, sa.ForeignKey(f"{users}.id"), nullable=False),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('indexed_at', sa.DateTime()),
    ]

    # Optional SQLAlchemy Table() instance kwargs
    schema_kwargs = {}
