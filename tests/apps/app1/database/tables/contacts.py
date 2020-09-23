import uvicore
import sqlalchemy as sa
from uvicore.database.table import Schema
from uvicore.support.dumper import dump


# Get related tablenames with proper prefixes
users = uvicore.db.tablename('auth.users')


class _Contacts(Schema):

    # Actual database table name
    # Plural table names and singluar model names are encouraged
    # Do not add a package prefix, leave that to the connection config
    name = 'contacts'

    # Connection for this database from your config file
    connection = 'app1'

    # SQLAlchemy Table definition as a list (exclude name and metadata)
    # This will be converted into an actual SQLAlchemy Table() instance
    # See https://docs.sqlalchemy.org/en/13/core/schema.html
    schema = [
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(length=100)),
        sa.Column('title', sa.String(length=100)),
        sa.Column('address', sa.String(length=100)),
        sa.Column('phone', sa.String(length=100)),
        sa.Column('user_id', sa.Integer, sa.ForeignKey(f"{users}.id"), nullable=False),
    ]

    # Optional SQLAlchemy Table() instance kwargs
    schema_kwargs = {
        'sqlite_autoincrement': True,
    }


# IoC Class Instance
Contacts: _Contacts = uvicore.ioc.make('app1.database.tables.contacts.Contacts', _Contacts, singleton=True)
