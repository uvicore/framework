import uvicore
from typing import Dict
from uvicore.contracts import Database as DatabaseInterface
from uvicore.support.dumper import dd, dump
from uvicore.contracts import Connection
from sqlalchemy import create_engine
from sqlalchemy import MetaData


class _Db(DatabaseInterface):

    # Class Variables
    default: str = None
    connections: Dict[str, Connection] = {}
    engines: Dict[str, str] = {}
    metadata: Dict[str, str] = {}

    @staticmethod
    def add_connection(connection: Connection) -> None:
        __class__.connections[connection.name] = connection
        __class__.engines[connection.name] = create_engine(connection.url)
        __class__.metadata[connection.name] = MetaData()

    # Instance Variables
    # @property
    # def default(self) -> str:
    #     return self._default

    # @property
    # def connections(self) -> Dict[str, Connection]:
    #     return self._connections

    # @property
    # def engines(self) -> Dict[str, str]:
    #     return self._engines

    # @property
    # def metadata(self) -> Dict[str, str]:
    #     return self._metadata

    # @default.setter
    # def default(self, value: str) -> None:
    #     self._default = value

    def __init__(self, connection: str = None):
        if not connection:
            connection = __class__.default
        #self._default = None
        #self._connections = {}
        #self._engines = {}
        #self._metadata = {}
        self._connection = connection
        self._table = None
        self._where = None

    def table(self, name: str):
        self._table = name
        return self

    def get(self):
        con = self._connect()
        query = self._query()
        results = con.execute(query)
        return results
        # rows = []
        # for row in results:
        #     rows.append(row)
        #     #rows.append(entity.User(**row))
        #     #rows.append(entity(**row))
        # return rows

    def _query(self):
        """Convert query builder into SQLAlechemy query"""
        #dd(__class__.metadata.get(self._connection).tables['users'])
        table = self._sa_table(self._table)
        query = table.select()
        return query

    def _sa_table(self, name: str):
        tables = __class__.metadata.get(self._connection).tables
        if name in tables:
            return tables.get(name)

    def _connect(self):
        return self.engine().connect()

    def engine(self):
        return __class__.engines.get(self._connection)


    # def _fetchall(self, entity, query) -> List[E]:
    #     if app.is_async:
    #         return self.encodedb.fetch_all(query=query)
    #     else:
    #         with self.connect() as con:
    #             results = con.execute(query)
    #             rows = []
    #             for row in results:
    #                 #rows.append(entity.User(**row))
    #                 rows.append(entity(**row))
    #             return rows


    # def _build_connection(self):
    #     if not 'connection' in self._query:
    #         self._query['connection'] = self.default




    # def add_connection(self, name: str, driver: str,
    #     dialect: str, host: str, port: int, database: str,
    #     username: str, password: str, prefix: str
    # ) -> None:
    #     url = (driver
    #         + '+' + dialect
    #         + '://' + username
    #         + ':' + password
    #         + '@' + host
    #         + ':' + str(port)
    #         + '/' + database)

    #     self._connections[name] = {
    #         'name': name,
    #         'driver': driver,
    #         'dialect': dialect,
    #         'host': host,
    #         'port': port,
    #         'url': url,
    #         'prefix': prefix
    #     }


# IoC Class Instance
# No, not a public API

# Public API for import * and doc gens
__all__ = ['_Db']
