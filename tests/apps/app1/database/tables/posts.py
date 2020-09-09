import sqlalchemy as sa
from uvicore.database.table import Schema

users = 'auth_users'


class Table(metaclass=Schema):

    # Actual database table name
    # Plural table names and singluar model names are encouraged
    # Do not add a package prefix, leave that to the connection config
    name = 'posts'

    # Connection for this database from your config file
    connection = 'app1'

    # SQLAlchemy Table definition as a list (exclude name and metadata)
    # This will be converted into an actual SQLAlchemy Table() instance
    # See https://docs.sqlalchemy.org/en/13/core/schema.html
    schema = [
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('unique_slug', sa.String(length=100), unique=True),
        sa.Column('title', sa.String(length=100)),
        sa.Column('other', sa.String(length=100), nullable=True),
        sa.Column('creator_id', sa.Integer, sa.ForeignKey(users + '.id'), nullable=False),
    ]

    # Optional SQLAlchemy Table() instance kwargs
    schema_kwargs = {
        'sqlite_autoincrement': True,
    }
