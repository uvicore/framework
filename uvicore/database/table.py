#from uvicore import db
#from sqlalchemy import Table as BaseTable
import sqlalchemy as sa


class Table:
    def __init__(self,
        name: str,
        connection: str,
        schema: sa.Table,
     ) -> None:
        self.name = name
        self.connection = connection
        self.schema = schema

autocolumns = [
    sa.Column('first_name', sa.String(length=50))
]


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
