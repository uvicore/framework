import uvicore
import sqlalchemy as sa
from uvicore.database.table import Schema, SchemaOLD
from uvicore.support.dumper import dump


# Get related tablenames with proper prefixes
posts = uvicore.db.tablename('app1.posts')
users = uvicore.db.tablename('auth.users')


@uvicore.table()
class Comments(Schema):
#class Table(metaclass=SchemaOLD):

    # Actual database table name
    # Plural table names and singluar model names are encouraged
    # Do not add a package prefix, leave that to the connection config
    name = 'comments'

    # Connection for this database from your config file
    connection = 'app1'

    # SQLAlchemy Table definition as a list (exclude name and metadata)
    # This will be converted into an actual SQLAlchemy Table() instance
    # See https://docs.sqlalchemy.org/en/13/core/schema.html
    schema = [
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('title', sa.String(length=100)),
        sa.Column('body', sa.Text()),
        sa.Column('post_id', sa.Integer, sa.ForeignKey(f"{posts}.id"), nullable=False),
        sa.Column('creator_id', sa.Integer, sa.ForeignKey(f"{users}.id"), nullable=False),
    ]

    # Optional SQLAlchemy Table() instance kwargs
    schema_kwargs = {
       #'sqlite_autoincrement': True,
    }


# IoC Class Instance
#Comments: _Comments = uvicore.ioc.make('app1.database.tables.comments.Comments', _Comments, singleton=True)
