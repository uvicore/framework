import uvicore
from uvicore import app
from typing import Dict, List
from uvicore.contracts import Connection
from uvicore.contracts import Database as DatabaseInterface
from uvicore.support.dumper import dd, dump
import sqlalchemy as sa
# from sqlalchemy import MetaData as SaMetaData
# from sqlalchemy.engine import Engine as SaEngine
# from sqlalchemy.engine import Connection as SaConnection
from databases import Database as EncodeDatabase
from asgiref.sync import async_to_sync
from uvicore.concurrency import asyncmethod


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
    def metadatas(self) -> Dict[str, sa.MetaData]:
        return self._metadatas

    @default.setter
    def default(self, value: str) -> None:
        self._default = value

    def __init__(self) -> None:
        self._default = None
        self._connections = {}
        self._engines = {}
        self._metadatas = {}

    def init(self, default: str, connections: List[Connection]) -> None:
        self._default = default
        for connection in connections:
            url = (connection.driver
                + '://' + connection.username
                + ':' + connection.password
                + '@' + connection.host
                + ':' + str(connection.port)
                + '/' + connection.database
            )
            self._connections[connection.name] = connection
            self._engines[connection.metakey] = EncodeDatabase(url)
            self._metadatas[connection.metakey] = sa.MetaData()

        # if app.is_http:
        #     @app.http.on_event("startup")
        #     async def startup():
        #         for engine in self.engines.values():
        #             await engine.connect()

        #     @app.http.on_event("shutdown")
        #     async def shutdown():
        #         for engine in self.engines.values():
        #             await engine.disconnect()

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
        engine = self.engines.get(metakey)  # Dont call self.engine() as its recursive
        if not engine.is_connected:
            await engine.connect()

    async def engine(self, connection: str = None, metakey: str = None) -> sa.engine.Engine:
        """Get one engine by connection name or metakey"""
        metakey = self.metakey(connection, metakey)
        await self.connect(metakey=metakey)
        return self.engines.get(metakey)

    async def fetchone(self, entity, query):
        engine = await self.engine(entity.__connection__)
        return await engine.fetch_one(query=query)

    #@asyncmethod
    async def fetchall(self, entity, query):
        #return self.execute(entity, query).fetchall()
        #await self.connect(entity.__connection__)
        engine = await self.engine(entity.__connection__)
        return await engine.fetch_all(query=query)

