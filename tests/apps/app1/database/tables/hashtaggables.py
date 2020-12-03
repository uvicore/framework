import uvicore
import sqlalchemy as sa
from uvicore.database import Table
from uvicore.support.dumper import dump


# Get related tablenames with proper prefixes
hashtags = uvicore.db.tablename('app1.hashtags')

@uvicore.table()
class Hashtaggables(Table):

    # Actual database table name
    # Plural table names and singluar model names are encouraged
    # Do not add a package prefix, leave that to the connection config
    name = 'hashtaggables'

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
        sa.Column('hashtaggable_type', sa.String(length=50)),
        sa.Column('hashtaggable_id', sa.Integer),

        sa.Column('hashtag_id', sa.Integer, sa.ForeignKey(f"{hashtags}.id"), nullable=False),

        # Multi Column Unique Constraint.  By adding in the key we still ensure
        # OneToMany can be used but it must be unique with the key.  This also creates
        # a good composite index of type,id,key
        sa.UniqueConstraint('hashtaggable_type', 'hashtaggable_id', 'hashtag_id')

        # If you don't want an ID primary_key, you could use the combined poly IDs as a PK
        # But the ORM can't handle duel PKs at the moment
        #sa.PrimaryKeyConstraint('hashtaggable_type', 'hashtaggable_id', 'key'),
    ]

    # Optional SQLAlchemy Table() instance kwargs
    schema_kwargs = {
        #'sqlite_autoincrement': True,
    }


# IoC Class Instance
#Attributes: _Attributes = uvicore.ioc.make('app1.database.tables.attributes.Attributes', _Attributes, singleton=True)
