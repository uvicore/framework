from typing import Any, AsyncGenerator, Dict, List, Mapping, Optional, Union

import sqlalchemy as sa
from databases import Database as EncodeDatabase
from sqlalchemy.sql import ClauseElement

import uvicore
from uvicore.contracts import Connection
from uvicore.contracts import Database as DatabaseInterface
from uvicore.database.query import _DbQueryBuilder
from uvicore.support.dumper import dd, dump
from sqlalchemy.engine.result import RowProxy

@uvicore.service('uvicore.database.db._Db',
    aliases=['Database', 'database', 'db'],
    singleton=True,
)
class _Db(DatabaseInterface):
    """Database private class.

    Do not import from this location.
    Use the uvicore.db singleton global instead."""

    @property
    def default(self) -> str:
        return self._default

    @property
    def connections(self) -> Dict[str, Connection]:
        return self._connections

    @property
    def engines(self) -> Dict[str, sa.engine.Engine]:
        return self._engines

    @property
    def databases(self) -> Dict[str, EncodeDatabase]:
        return self._databases

    @property
    def metadatas(self) -> Dict[str, sa.MetaData]:
        return self._metadatas

    def __init__(self) -> None:
        self._default = None
        self._connections = {}
        self._engines = {}
        self._databases = {}
        self._metadatas = {}

    def init(self, default: str, connections: List[Connection]) -> None:
        self._default = default
        for connection in connections:
            # connection.url has a dialect in it, which we need for engines
            # but don't need for encode/databases library
            if connection.driver == 'sqlite':
                encode_url = (connection.driver
                    + ':///' + connection.database
                )
            else:
                encode_url = (connection.driver
                    + '://' + connection.username
                    + ':' + connection.password
                    + '@' + connection.host
                    + ':' + str(connection.port)
                    + '/' + connection.database
                )
            self._connections[connection.name] = connection
            self._engines[connection.metakey] = sa.create_engine(connection.url)
            self._databases[connection.metakey] = EncodeDatabase(encode_url)
            self._metadatas[connection.metakey] = sa.MetaData()

        if uvicore.app.is_http:
            @uvicore.app.http.on_event("startup")
            async def startup():
                for database in self.databases.values():
                    await database.connect()

            @uvicore.app.http.on_event("shutdown")
            async def shutdown():
                for database in self.databases.values():
                    await database.disconnect()

    def packages(self, connection: str = None, metakey: str = None) -> Connection:
        if not metakey:
            if not connection: connection = self.default
            metakey = self.connection(connection).metakey
        packages = []
        for package in uvicore.app.packages.values():
            for conn in package.connections:
                if conn.metakey == metakey:
                    packages.append(package)
        return packages

    def metakey(self, connection: str = None, metakey: str = None) -> str:
        try:
            if not metakey:
                if not connection: connection = self.default
                metakey = self.connection(connection).metakey
            return metakey
        except Exception:
            raise Exception('Metakey not found, connection={} metakey={}'.format(connection, metakey))

    def connection(self, connection: str = None) -> Connection:
        if not connection: connection = self.default
        return self.connections.get(connection)

    def metadata(self, connection: str = None, metakey: str = None) -> sa.MetaData:
        metakey = self.metakey(connection, metakey)
        return self.metadatas.get(metakey)

    def table(self, table: str, connection: str = None) -> sa.Table:
        tablename = self.tablename(table, connection)
        metadata = self.metadata(connection)
        if metadata: return metadata.tables.get(tablename)

    def tablename(self, table: str, connection: str = None) -> str:
        if '.' in table:
            connection, table = tuple(table.split('.'))
        connection = self.connection(connection)
        if connection:
            return connection.prefix + table

    def engine(self, connection: str = None, metakey: str = None) -> sa.engine.Engine:
        metakey = self.metakey(connection, metakey)
        return self.engines.get(metakey)

    async def database(self, connection: str = None, metakey: str = None) -> EncodeDatabase:
        metakey = self.metakey(connection, metakey)
        database = self.databases.get(metakey)
        if not database.is_connected:
            await database.connect()
        #await self._connect(metakey=metakey)
        return self.databases.get(metakey)

    async def disconnect(self, connection: str = None, metakey: str = None) -> None:
        metakey = self.metakey(connection, metakey)
        database = self.databases.get(metakey)
        if database.is_connected:
            await database.disconnect()

    async def disconnect_all(self):
        for database in self.databases.keys():
            await self.disconnect(metakey=database)

    async def fetchall(self, query: Union[ClauseElement, str], values: Dict = None, connection: str = None, metakey: str = None) -> List[RowProxy]:
        database = await self.database(connection, metakey)
        return await database.fetch_all(query, values)

    async def fetchone(self, query: Union[ClauseElement, str], values: Dict = None, connection: str = None, metakey: str = None) -> Optional[RowProxy]:
        database = await self.database(connection, metakey)
        return await database.fetch_one(query, values)

    async def execute(self, query: Union[ClauseElement, str], values: Union[List, Dict] = None, connection: str = None, metakey: str = None) -> Any:
        database = await self.database(connection, metakey)
        if type(values) == dict:
            return await database.execute(query, values)
        elif type(values) == list:
            return await database.execute_many(query, values)
        else:
            return await database.execute(query)

    #  async def iterate(self, query: Union[ClauseElement, str], values: dict = None, connection: str = None) -> AsyncGenerator[Mapping, None]:
    #     async with self.connection() as connection:
    #         async for record in connection.iterate(query, values):
    #             yield record

    # async def _connect(self, connection: str = None, metakey: str = None) -> None:
    #     # Async connect to db if not connected
    #     # If running from web, we will already be connected from on_event("startup")
    #     # but if from CLI, we wont
    #     metakey = self.metakey(connection, metakey)
    #     database = self.databases.get(metakey)  # Dont call self.database() as its recursive
    #     if not database.is_connected:
    #         await database.connect()


    def query(self, connection: str = None) -> _DbQueryBuilder[_DbQueryBuilder, Any]:
        if not connection: connection = self.default
        return _DbQueryBuilder(connection)


    # def table(self, table: str):
    #     return QueryBuilder(self, self.default, table)

    # def conn(self, connection: str):
    #     return QueryBuilder(self, connection)


# IoC Class Instance
# Not to be imported by the public from here.
# Use the uvicore.db singleton global instead.
















#class QueryBuilder:
#     def __init__(self, db: DatabaseInterface, connection: str, table: str = None):
#         self.db = db
#         self.connection = connection or self.db.default
#         self.prefix = self.db.connection(self.connection).prefix
#         self._table = table
#         self._join = None
#         self._select = None
#         self._where = []

#     def table(self, table: str):
#         self._table = self.prefix + table
#         return self

#     def select(self, *args):
#         self._select = args
#         return self

#     def join(self, table: str, left: str, operator: str, right: str):
#         dd('hi')

#     def where(self, column: str, operator: str = None, value: Any = None):
#         if not value:
#             value = operator
#             operator = '='
#         self._where.append((column, operator, value))
#         return self

#     # Finalizers are find, get, update, delete, insert

#     async def find(self, pk: Any):
#         # FIDME, need dynamic pk
#         table, query = self.build()
#         query = query.where(table.c.id == pk)
#         return await self.db.fetchone(query)

#     async def get(self):
#         table, query = self.build()

#         # if self._select is none
#         # query = sa.select([table.c.id, table.c.email])
#         # #query = table.select()

#         #x = [getattr(table.c, x) for x in self._select]
#         #return x

#         return await self.db.fetchall(query)
#         return {
#             'db': self.db,
#             'connection': self.db.connection(self.connection),
#             'select': self._select,
#             'table': table,
#             'where': self._where,
#         }

#     def build(self, method: str = 'select'):
#         table = self.get_table()
#         query = None

#         # where
#         #   select
#         #   update (not in insert)
#         #   delete

#         if method == 'select':
#             if self._select:
#                 columns = []
#                 #for select in self._select:
#                 columns = [getattr(table.c, x) for x in self._select]
#                 query = sa.select(columns)
#             else:
#                 query = sa.select([table])

#         return table, query

#     def get_table(self):
#         #return self.db.table(self._table, connection=self.connection)
#         metadata = self.db.metadata(self.connection)
#         if metadata:
#             return metadata.tables.get(self._table)

#adf
