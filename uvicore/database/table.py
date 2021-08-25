import uvicore
import sqlalchemy as sa
from abc import ABCMeta
from typing import Dict, List
from uvicore.support.dumper import dd, dump

@uvicore.service()
class Table:

    @property
    def table(self):
        return self.schema

    def __init__(self):
        # Tables are singleton classes bound in the IoC
        # So they are instantiated ONCE when first ioc.make()
        # Once instantiated, the actual SQLAlchemy table is created
        # and added to the metadata.  Tables cannot be made twice or SA
        # complains about duplicate tables.  To override a table simply use
        # your app configs bindings array to swap the initial singleton binding.
        self.metadata = uvicore.db.metadata(self.connection)
        prefix = uvicore.db.connection(self.connection).prefix
        if prefix is not None:
            self.name = str(prefix) + self.name

        # Only enhance schema if connection string backend is 'sqlalchemy'
        if uvicore.db.connection(self.connection).backend == 'sqlalchemy':
            self.schema = sa.Table(
                self.name,
                self.metadata,
                *self.schema,
                **self.schema_kwargs
            )


# class SchemaOLD(ABCMeta):
#     def __new__(mcs, name, bases, namespace, **kwargs):
#         # Set metadata based on connection string
#         namespace['metadata'] = uvicore.db.metadata(namespace.get('connection'))

#         # Add prefix to table name
#         prefix = uvicore.db.connection(namespace.get('connection')).prefix
#         if prefix is not None:
#             namespace['name'] = str(prefix) + namespace['name']

#         # Convert table List into actual SQLAlchemy table schema
#         namespace['schema'] = sa.Table(
#             namespace['name'],
#             namespace['metadata'],
#             *namespace['schema'],
#             **namespace.get('schema_kwargs')
#         )

#         # Return this new metaclass
#         return super().__new__(mcs, name, bases, namespace, **kwargs)

# class Table:
#     def __init__(self,
#         name: str,
#         connection: str,
#         schema: sa.Table,
#      ) -> None:
#         self.name = name
#         self.connection = connection
#         self.schema = schema

# autocolumns = [
#     sa.Column('first_name', sa.String(length=50))
# ]


# class Table(BaseTable):
#     """A simple SQLAlchemy Table abstraction that allows you to specify
#     a connection string instead of metedata.  Metadata is derived from
#     this connection string.  Connection string now available at yourtable.connection
#     """
#     def __new__(cls, name: str, connection: str, *args, **kwargs):
#         return super().__new__(cls, name, db.metadata.get(connection), *args, *kwargs)

#     def __init__(self, name: str, connection: str, *args, **kwargs) -> None:
#         # Don't set self.name, it already exists in BaseTable
#         # We are only adding a connection property to the already large
#         # BaseTable dictionary
#         self.connection = connection
#         super().__init__(self, name, db.metadata.get(connection), *args, **kwargs)
