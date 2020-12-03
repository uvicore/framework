from abc import ABC, abstractmethod
from typing import Any, Dict, List, Union, Mapping, Optional

import sqlalchemy as sa
from databases import Database as EncodeDatabase
from sqlalchemy.sql import ClauseElement
from uvicore.contracts import DbQueryBuilder

from .connection import Connection
from .package import Package


class Database(ABC):
    pass

    @property
    @abstractmethod
    def default(self) -> str:
        """The default connection str for the main running app"""
        pass

    @property
    @abstractmethod
    def connections(self) -> Dict[str, Connection]:
        """All connections from all packages, keyed by connection str name"""
        pass

    @property
    @abstractmethod
    def engines(self) -> Dict[str, sa.engine.Engine]:
        """All engines for all unique (by metakey) connections, keyed by metakey"""
        pass

    @property
    @abstractmethod
    def databases(self) -> Dict[str, EncodeDatabase]:
        """All Encode Databases for all unique (by metakey) connections, keyed by metakey"""
        pass

    @property
    @abstractmethod
    def metadatas(self) -> Dict[str, sa.MetaData]:
        """All SQLAlchemy Metadata for all unique (by metakey) connections, keyed by metakey"""
        pass

    @abstractmethod
    def init(self, default: str, connections: List[Connection]) -> None:
        """Initialize the database system with a default connection str and List of all Connections from all packages"""
        pass

    @abstractmethod
    def packages(self, connection: str = None, metakey: str = None) -> List[Package]:
        """Get all packages with the metakey (direct or derived from connection str)."""
        pass

    @abstractmethod
    def metakey(self, connection: str = None, metakey: str = None) -> str:
        """Get one metekay by connection str or metakey"""
        pass

    @abstractmethod
    def connection(self, connection: str = None) -> Connection:
        """Get one connection by connection name"""
        pass

    @abstractmethod
    def metadata(self, connection: str = None, metakey: str = None) -> sa.MetaData:
        """Get one SQLAlchemy Metadata by connection str or metakey"""
        pass

    @abstractmethod
    def table(self, table: str, connection: str = None) -> sa.Table:
        """Get one SQLAlchemy Table by name (without prefix) and connection str or connection.tablename dot notation"""
        pass

    @abstractmethod
    def tablename(self, table: str, connection: str = None) -> str:
        """Get a SQLAlchemy tablename with prefix by name (without prefix) and connection str or connection.tablename dot notation"""
        pass

    @abstractmethod
    def engine(self, connection: str = None, metakey: str = None) -> sa.engine.Engine:
        """Get one SQLAlchemy Engine by connection str or metakey"""
        pass

    @abstractmethod
    async def database(self, connection: str = None, metakey: str = None) -> EncodeDatabase:
        """Get one Encode Database by connection str or metakey"""
        pass

    @abstractmethod
    async def disconnect(self, connection: str = None, metakey: str = None) -> None:
        """Disconnect from database by connection str or metakey"""
        pass

    @abstractmethod
    async def disconnect_all(self):
        """Disconnect from all connected databases"""
        pass

    @abstractmethod
    async def fetchall(self, query: Union[ClauseElement, str], values: Dict = None, connection: str = None, metakey: str = None) -> List[Mapping]:
        """Fetch List of records from a SQLAlchemy Core Query based on connection str or metakey"""
        pass

    @abstractmethod
    async def fetchone(self, query: Union[ClauseElement, str], values: Dict = None, connection: str = None, metakey: str = None) -> Optional[Mapping]:
        """Fetch one record from a SQLAlchemy Core Query based on connection str or metakey"""
        pass

    @abstractmethod
    async def execute(self, query: Union[ClauseElement, str], values: Union[List, Dict] = None, connection: str = None, metakey: str = None) -> Any:
        """Execute a SQLAlchemy Core Query based on connection str or metakey"""
        pass

    @abstractmethod
    def query(self, connection: str = None) -> DbQueryBuilder[DbQueryBuilder, None]:
        """Database query builder passthrough"""

    # @property
    # @abstractmethod
    # def events(self) -> Dict: pass

    # @property
    # @abstractmethod
    # def listeners(self) -> Dict[str, List]: pass

    # @property
    # @abstractmethod
    # def wildcards(self) -> List: pass

    # @abstractmethod
    # def register(self, events: Dict):
    #     pass

    # @abstractmethod
    # def listen(self, events: Union[str, List], listener: Any) -> None:
    #     pass

    # @abstractmethod
    # def dispatch(self, event: Any, payload = {}) -> None:
    #     pass

    # @abstractmethod
    # def get_listeners(self, event: str) -> List:
    #     pass
