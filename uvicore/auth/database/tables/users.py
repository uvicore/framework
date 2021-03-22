import sqlalchemy as sa

import uvicore
from uvicore.database import Table
from uvicore.support.dumper import dd, dump


# Get related tablenames with proper prefixes
users = uvicore.db.tablename('auth.users')

@uvicore.table()
class Users(Table):

    # Actual database table name
    # Plural table names and singluar model names are encouraged
    # Do not add a package prefix, leave that to the connection config
    name = 'users'

    # Connection for this database from your config file
    connection = 'auth'

    # SQLAlchemy Table definition as a list (exclude name and metadata)
    # This will be converted into an actual SQLAlchemy Table() instance
    # See https://docs.sqlalchemy.org/en/13/core/schema.html
    schema = [
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('uuid', sa.String(length=36), unique=True),
        sa.Column('username', sa.String(length=50), unique=True),
        sa.Column('email', sa.String(length=50), unique=True),
        sa.Column('first_name', sa.String(length=30)),
        sa.Column('last_name', sa.String(length=30)),
        sa.Column('title', sa.String(length=50)),
        sa.Column('avatar_url', sa.String(length=500)),
        sa.Column('password', sa.Text()),
        sa.Column('disabled', sa.Boolean, default=False),
        sa.Column('creator_id', sa.Integer, sa.ForeignKey(f"{users}.id")),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('login_at', sa.DateTime, nullable=True),


        # 10 dddddddddd
        # 20 dddddddddddddddddddd
        # 30 dddddddddddddddddddddddddddddd
        # 40 dddddddddddddddddddddddddddddddddddddddd
        # 50 dddddddddddddddddddddddddddddddddddddddd
        # 100 dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd
        # 200 dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd

    ]

    # Optional SQLAlchemy Table() instance kwargs
    schema_kwargs = {}
