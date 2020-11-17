import uvicore
import sqlalchemy as sa
from uvicore.database.table import Schema
from uvicore.support.dumper import dump


class _Images(Schema):

    # Actual database table name
    # Plural table names and singluar model names are encouraged
    # Do not add a package prefix, leave that to the connection config
    name = 'images'

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
        sa.Column('imageable_type', sa.String(length=50)),
        sa.Column('imageable_id', sa.Integer),

        # Image data
        sa.Column('filename', sa.String(length=100)),
        sa.Column('size', sa.Integer),

        # Multi Column Unique Constraint, this ensures a true One-To-One
        # and creates a composite index in the given order.
        # This forced uniqueness is what makes the table slightly different than a One-To-Many table.
        sa.UniqueConstraint('imageable_type', 'imageable_id')

        # If you don't want an ID primary_key, you could use the combined poly IDs as a PK
        #sa.PrimaryKeyConstraint('imageable_type', 'imageable_id'),
    ]

    # Optional SQLAlchemy Table() instance kwargs
    schema_kwargs = {
        #'sqlite_autoincrement': True,
    }


# IoC Class Instance
Images: _Images = uvicore.ioc.make('app1.database.tables.images.Images', _Images, singleton=True)
