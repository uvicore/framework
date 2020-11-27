import uvicore
import sqlalchemy as sa
from uvicore.database.table import Schema
from uvicore.support.dumper import dump


# Get related tablenames with proper prefixes
#users = uvicore.db.tablename('auth.users')

@uvicore.table()
class Attributes(Schema):

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
        # Having an ID on a poly table ensures the clustered data is still inserted in order
        # If we had no ID and clustered on imageable_id + imageable_type data would be re-ordered on insert
        sa.Column('id', sa.Integer, primary_key=True),

        # Polymorphic Relations
        sa.Column('attributable_type', sa.String(length=50)),
        sa.Column('attributable_id', sa.Integer),

        sa.Column('key', sa.String(length=100)),
        sa.Column('value', sa.Text()),

        # Multi Column Unique Constraint.  By adding in the key we still ensure
        # OneToMany can be used but it must be unique with the key.  This also creates
        # a good composite index of type,id,key
        sa.UniqueConstraint('attributable_type', 'attributable_id', 'key')

        # If you don't want an ID primary_key, you could use the combined poly IDs as a PK
        #sa.PrimaryKeyConstraint('attributable_type', 'attributable_id', 'key'),
    ]

    # Optional SQLAlchemy Table() instance kwargs
    schema_kwargs = {
        #'sqlite_autoincrement': True,
    }


# IoC Class Instance
#Attributes: _Attributes = uvicore.ioc.make('app1.database.tables.attributes.Attributes', _Attributes, singleton=True)
