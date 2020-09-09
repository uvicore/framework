import uvicore
from typing import Dict, List
from uvicore.contracts import Connection
from uvicore.contracts import Database as DatabaseInterface
from uvicore.support.dumper import dd, dump
import sqlalchemy as sa
# from sqlalchemy import MetaData as SaMetaData
# from sqlalchemy.engine import Engine as SaEngine
# from sqlalchemy.engine import Connection as SaConnection


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
            self._connections[connection.name] = connection
            self._engines[connection.metakey] = sa.create_engine(connection.url)
            self._metadatas[connection.metakey] = sa.MetaData()

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

    def connection(self, connection: str = None) -> Connection:
        """Get one connection by connection name"""
        if not connection: connection = self.default
        return self.connections.get(connection)

    def metadata(self, connection: str = None, metakey: str = None) -> sa.MetaData:
        """Get one metadata by connection name or metakey"""
        if metakey:
            return self.metadatas.get(metakey)
        else:
            if not connection: connection = self.default
            metakey = self.connection(connection).metakey
            return self.metadatas.get(metakey)

    def engine(self, connection: str = None, metakey: str = None) -> sa.engine.Engine:
        """get one engine by connection name or metakey"""
        if metakey:
            return self.engines.get(metakey)
        else:
            if not connection: connection = self.default
            metakey = self.connection(connection).metakey
            return self.engines.get(metakey)

    def connect(self, connection: str = None, metakey: str = None) -> sa.engine.Connection:
        """Connect to one engine by connection name or metakey"""
        if metakey:
            return self.engine(metakey=metakey).connect()
        else:
            if not connection: connection = self.default
            return self.engine(connection).connect()

    def execute(self, entity, *args, **kwargs):
        conn = self.connect(entity.__connection__)
        return conn.execute(*args, **kwargs)

    def fetchone(self, entity, query):
        return self.execute(entity, query).fetchone()

    def fetchall(self, entity, query):
        return self.execute(entity, query).fetchall()



