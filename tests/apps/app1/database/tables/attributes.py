import uvicore
import sqlalchemy as sa
from uvicore.database.table import Schema
from uvicore.support.dumper import dump


# Get related tablenames with proper prefixes
#users = uvicore.db.tablename('auth.users')

class _Attributes(Schema):

    # Actual database table name
    # Plural table names and singluar model names are encouraged
    # Do not add a package prefix, leave that to the connection config
    name = 'attributes'

    # Connection for this database from your config file
    connection = 'app1'

    # SQLAlchemy Table definition as a list (exclude name and metadata)
    # This will be converted into an actual SQLAlchemy Table() instance
    # See https://docs.sqlalchemy.org/en/13/core/schema.html
    schema = [
        #sa.Column('id', sa.Integer, primary_key=True),
        # Polymorphic Relations
        sa.Column('table_name', sa.String(length=50)),
        sa.Column('table_pk', sa.Integer),

        sa.Column('key', sa.String(length=100)),
        sa.Column('value', sa.Text()),

        # Multi Column Unique Key Constraint
        sa.PrimaryKeyConstraint('table_name', 'table_pk', 'key'),
    ]

    # Optional SQLAlchemy Table() instance kwargs
    schema_kwargs = {
        #'sqlite_autoincrement': True,
    }


# IoC Class Instance
Attributes: _Attributes = uvicore.ioc.make('app1.database.tables.attributes.Attributes', _Attributes, singleton=True)
