import uvicore
from uvicore import app
from typing import Dict, List, Any, Union
from uvicore.contracts import Connection
from uvicore.contracts import Database as DatabaseInterface
from uvicore.support.dumper import dd, dump
import sqlalchemy as sa
# from sqlalchemy import MetaData as SaMetaData
# from sqlalchemy.engine import Engine as SaEngine
# from sqlalchemy.engine import Connection as SaConnection
from databases import Database as EncodeDatabase


class _Db(DatabaseInterface):

    @property
    def default(self) -> str:
        return self._default

    @property
    def connections(self) -> Dict[str, Connection]:
        return self._connections

    @property
    def engines(self) -> Dict[str, str]:
        return self._engines

    @property
    def databases(self) -> Dict[str, str]:
        return self._databases

    @property
    def metadatas(self) -> Dict[str, sa.MetaData]:
        return self._metadatas

    @default.setter
    def default(self, value: str) -> None:
        self._default = value

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

        # if app.is_http:
        #     @app.http.on_event("startup")
        #     async def startup():
        #         for database in self.databases.values():
        #             await database.connect()

        #     @app.http.on_event("shutdown")
        #     async def shutdown():
        #         for database in self.databases.values():
        #             await database.disconnect()

    def packages(self, connection: str = None, metakey: str = None) -> Connection:
        """Get all packages with the metakey derived from the connection name
        or passed in metakey.
        """
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
        if not metakey:
            if not connection: connection = self.default
            metakey = self.connection(connection).metakey
        return metakey

    def connection(self, connection: str = None) -> Connection:
        """Get one connection by connection name"""
        if not connection: connection = self.default
        return self.connections.get(connection)

    def metadata(self, connection: str = None, metakey: str = None) -> sa.MetaData:
        """Get one metadata by connection name or metakey"""
        metakey = self.metakey(connection, metakey)
        return self.metadatas.get(metakey)

    async def connect(self, connection: str = None, metakey: str = None) -> None:
        # Async connect to db if not connected
        # If running from web, we will already be connected from on_event("startup")
        # but if from CLI, we wont
        metakey = self.metakey(connection, metakey)
        database = self.databases.get(metakey)  # Dont call self.database() as its recursive
        if not database.is_connected:
            await database.connect()

    async def engine(self, connection: str = None, metakey: str = None) -> sa.engine.Engine:
        """Get one engine by connection name or metakey"""
        metakey = self.metakey(connection, metakey)
        return self.engines.get(metakey)

    async def database(self, connection: str = None, metakey: str = None) -> sa.engine.Engine:
        """Get one database by connection name or metakey"""
        metakey = self.metakey(connection, metakey)
        await self.connect(metakey=metakey)
        return self.databases.get(metakey)

    async def execute(self, query: Any, values: Union[List,Dict] = None, connection: str = None) -> Any:
        database = await self.database(connection)
        if type(values) == dict:
            return await database.execute(query, values)
        elif type(values) == list:
            return await database.execute_many(query, values)
        else:
            return await database.execute(query)

    # async def execute_many(self, query: Any, values: List, connection: str = None) -> None:
    #     database = await self.database(connection)
    #     return await database.execute_many(query, values)

    async def fetchone(self, query, connection: str = None):
        database = await self.database(connection)
        return await database.fetch_one(query=query)

    async def fetchall(self, query, connection: str = None):
        database = await self.database(connection)
        return await database.fetch_all(query=query)

