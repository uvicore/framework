import sqlalchemy as sa
from uvicore import db
from uvicore.database.table import Table, autocolumns
from uvicore.support.dumper import dump, dd

# Actual database table name
# Usually tabkes are plural while models are signular
tablename = 'users'

# Connection for this database from your config file
connection = 'auth'

# SQLAlchemy connection metedata this table belongs to
metadata = db.metadata.get(connection)

# Table object details
table = Table(tablename, connection,
    # Actual SQLAlchemy Table definition
    # See https://docs.sqlalchemy.org/en/13/core/schema.html
    schema=sa.Table(tablename, metadata,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("email", sa.String(length=50))

        # Automatically add owner_id, creator_id, updator_id,
        # created_at, updated_at columns required for Uvicore auth and logging
        #*autocolumns
    ),
)


# table = Table('users', 'auth',
#     # Actual SQLAlchemy Table definition
#     # See https://docs.sqlalchemy.org/en/13/core/schema.html
#     sa.Column("id", sa.Integer, primary_key=True),
#     sa.Column("email", sa.String(length=50))

#     # Automatically add owner_id, creator_id, updator_id,
#     # created_at, updated_at columns required for Uvicore auth and logging
#     #*autocolumns
# )
