import uvicore
import sqlalchemy as sa
from uvicore.database import Table
from uvicore.support.dumper import dump


# Get related tablenames with proper prefixes
posts = uvicore.db.tablename('app1.posts')
tags = uvicore.db.tablename('app1.tags')


@uvicore.table()
class PostTags(Table):
#class Table(metaclass=SchemaOLD):

    # Actual database table name
    # Plural table names and singluar model names are encouraged
    # Do not add a package prefix, leave that to the connection config
    name = 'post_tags'

    # Connection for this database from your config file
    connection = 'app1'

    # SQLAlchemy Table definition as a list (exclude name and metadata)
    # This will be converted into an actual SQLAlchemy Table() instance
    # See https://docs.sqlalchemy.org/en/13/core/schema.html
    schema = [
        sa.Column('post_id', sa.Integer, sa.ForeignKey(f"{posts}.id"), nullable=False),
        sa.Column('tag_id', sa.Integer, sa.ForeignKey(f"{tags}.id"), nullable=False),
        sa.PrimaryKeyConstraint('post_id', 'tag_id')
    ]

    # Optional SQLAlchemy Table() instance kwargs
    schema_kwargs = {
        #'sqlite_autoincrement': True,
    }


# IoC Class Instance
#PostTags: _PostTags = uvicore.ioc.make('app1.database.tables.post_tags.PostTags', _PostTags, singleton=True)
