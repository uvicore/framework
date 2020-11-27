import uvicore
import sqlalchemy as sa
from uvicore.database.table import Schema, SchemaOLD
from uvicore.support.dumper import dump, dd


#import sys
#dump(sys.modules)
#base = sys.modules['uvicore.auth.database.tables_BASE']
#from uvicore.auth.database.tables.users_BASE import Users as BaseUser
#dump(base)
# base_schema = [
#     sa.Column("id", sa.Integer, primary_key=True),
#     sa.Column("email", sa.String(length=50))
# ]


BaseUsers = uvicore.ioc.make('uvicore.auth.database.tables.users.Users_BASE')
base_schema = BaseUsers.schema



# @uvicore.table()
# def tablexyz():
#     pass


# This is an override.  Do not import this Table, instead import
# the original in uvicore.auth.database.tables
@uvicore.table()
class Users(Schema):

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
        # Include original auth users table
        #*users._Users.schema,
        *base_schema,

        # Add extra columns
        sa.Column("app1_extra", sa.String(length=50))
    ]

    # Optional SQLAlchemy Table() instance kwargs
    schema_kwargs = {
        #'sqlite_autoincrement': True,
    }



# IoC Class Instance
#Users: _Users = uvicore.ioc.make('uvicore.auth.database.tables.users.Users', _Users, singleton=True)

