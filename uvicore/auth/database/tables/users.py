import sqlalchemy as sa

import uvicore
from uvicore.database import Table
from uvicore.support.dumper import dd, dump


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
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("email", sa.String(length=50))
    ]

    # Optional SQLAlchemy Table() instance kwargs
    schema_kwargs = {}

#Users = Users()
# IoC Class Instance
#Users = _Users
#Users: _Users = uvicore.ioc.make('uvicore.auth.database.tables.users.Users', _Users, singleton=True)
