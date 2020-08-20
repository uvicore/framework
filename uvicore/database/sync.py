import uvicore
from typing import Dict, List
from uvicore.contracts import Connection
from uvicore.contracts import Database as DatabaseInterface
from uvicore.support.dumper import dd, dump
import sqlalchemy as sa
# from sqlalchemy import MetaData as SaMetaData
# from sqlalchemy.engine import Engine as SaEngine
# from sqlalchemy.engine import Connection as SaConnection


class _Sync(DatabaseInterface):

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
    def metadata(self) -> Dict[str, sa.MetaData]:
        return self._metadata

    @default.setter
    def default(self, value: str) -> None:
        self._default = value

    def __init__(self) -> None:
        self._default = None
        self._connections = {}
        self._engines = {}
        self._metadata = {}

    def init(self, default: str, connections: List[Connection]) -> None:
        self._default = default
        for connection in connections:
            self._connections[connection.name] = connection
            self._engines[connection.name] = sa.create_engine(connection.url)
            self._metadata[connection.name] = sa.MetaData()

    def execute(self, entity, query):
        #conn = self.connect(entity.Db.connection)
        conn = self.connect(entity.__connection__)
        return conn.execute(query)

    def fetchone(self, entity, query):
        return self.execute(entity, query).fetchone()

    def fetchall(self, entity, query):
        return self.execute(entity, query).fetchall()

    def connect(self, connection: str = None) -> sa.engine.Connection:
        if not connection: connection = self.default
        return self.engine(connection).connect()

    def engine(self, connection: str = None) -> sa.engine.Engine:
        if not connection: connection = self.default
        return self.engines.get(connection)

