import uvicore
import sqlalchemy as sa
from uvicore.database import Table
from uvicore.support.dumper import dump, dd


# Get related table names with proper prefixes
# users = uvicore.db.tablename('auth.users')
# formats = uvicore.db.tablename('xx_appname.formats')


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
        # Defaults: nullable=True, index=False, unique=False, primary_key=False

        sa.Column('id', sa.Integer, primary_key=True),  # SQL auto incrementing primary key int(11) datatype, the "clustered"index
        sa.Column('slug', sa.String(length=100), unique=True),  # SQL varchar(100) with unique index
        sa.Column('title', sa.String(length=100)),  # SQL varchar(100) datatype

        # sa.Column('key', sa.CHAR(length=3), primary_key=True),  # SQL non-incrementing primary key char(3) datatype, the "clustered"index

        # sa.Column('body', sa.Text()),  # SQL text datatype

        # sa.Column('view_count', sa.Integer),  # SQL int(11) datatype
        # sa.Column('view_count', sa.CHAR(length=3)),  # SQL char(4) datatype
        # sa.Column('dollar_amt', sa.DECIMAL(precision=8, scale=2)),  # SQL decimal(8,2) datatype max 999,999.99
        # sa.Column('dollar_amt2', sa.Float()),  # SQL Float datatype

        # sa.Column('is_deleted', sa.Boolean(), default=False),  # SQL tinyint(1) datatype

        # sa.Column('created_at', sa.DateTime()), # SQL datetime datatype
        # sa.Column('updated_at', sa.DateTime()), # SQL datetime datatype

        # sa.Column('format', sa.Integer, sa.ForeignKey(f"{formats}.id"), nullable=False),   # SQL Foreign key, which does create an index
        # sa.Column('creator_id', sa.Integer, sa.ForeignKey(f"{users}.id"), nullable=False), # SQL Foreign key, which does create an index
        # sa.Column('updator_id', sa.Integer, sa.ForeignKey(f"{users}.id"), nullable=False), # SQL Foreign key, which does create an index

        # Multi Column Unique Constraint.  By adding in the key we still ensure
        # OneToMany can be used but it must be unique with the key.  This also creates
        # a good composite index of type,id,key
        # sa.UniqueConstraint('attributable_type', 'attributable_id', 'key'),

        # If you don't want an ID primary_key, you could use the combined poly IDs as a PK
        # But the ORM can't handle duel PKs at the moment
        # sa.PrimaryKeyConstraint('attributable_type', 'attributable_id', 'key'),
    ]

    # Optional SQLAlchemy Table() instance kwargs
    schema_kwargs = {}
