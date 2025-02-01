from .package import Package
from .connection import Connection
from abc import ABC, abstractmethod
from uvicore.contracts import DbQueryBuilder
from uvicore.typing import Any, Dict, List, Sequence, Mapping, Optional

# Optional imports based on installed modules
try:
    import sqlalchemy as sa
except ImportError:
    pass


class Database(ABC):

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
    def metadatas(self) -> Dict[str, sa.MetaData]:
        """All SQLAlchemy Metadata for all unique (by metakey) connections, keyed by metakey"""
        pass

    @abstractmethod
    def init(self, default: str, connections: Dict[str, Connection]) -> None:
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
    def tables(self, connection: str = None, metakey: str = None) -> List[sa.Table]:
        """Get all SQLAlchemy tables for a given connection str or metakey"""
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
    def query(self, connection: str = None) -> DbQueryBuilder[DbQueryBuilder, Any]:
        """Database query builder passthrough"""


    @abstractmethod
    async def execute(
        self,
        query: Any,
        values: Optional[Sequence[Mapping[str, Any]] | Mapping[str, Any]] = None,
        connection: Optional[str] = None,
        metakey: Optional[str] = None
    ) -> sa.CursorResult:
        """Execute a SQLAlchemy Core Query based on connection str or metakey"""
        pass


    @abstractmethod
    async def all(self,
        query: sa.Select|str,
        values: Optional[Sequence[Mapping[str, Any]] | Mapping[str, Any]] = None,
        connection: Optional[str] = None,
        metakey: Optional[str] = None
    ) -> Sequence[sa.Row]:
        """Get many records from query. Returns empty List if no records found"""
        pass

    @abstractmethod
    async def fetchall(self,
        query: sa.Select|str,
        values: Optional[Sequence[Mapping[str, Any]] | Mapping[str, Any]] = None,
        connection: Optional[str] = None,
        metakey: Optional[str] = None
    ) -> Sequence[sa.Row]:
        """Alias to .all()"""
        pass

    @abstractmethod
    async def first(self,
        query: sa.Select|str,
        values: Optional[Sequence[Mapping[str, Any]] | Mapping[str, Any]] = None,
        connection: Optional[str] = None,
        metakey: Optional[str] = None
    ) -> sa.Row|None:
        """Get one (first/top) record from query. Returns None if no records found"""
        pass

    @abstractmethod
    async def fetchone(self,
        query: sa.Select|str,
        values: Optional[Sequence[Mapping[str, Any]] | Mapping[str, Any]] = None,
        connection: Optional[str] = None,
        metakey: Optional[str] = None
    ) -> sa.Row|None:
        """Alias to .first()"""
        pass

    @abstractmethod
    async def one(self,
        query: sa.Select|str,
        values: Optional[Sequence[Mapping[str, Any]] | Mapping[str, Any]] = None,
        connection: Optional[str] = None,
        metakey: Optional[str] = None
    ) -> sa.Row:
        """Get one record from query. Throws Exception if no data found or querying more than one record"""
        pass

    @abstractmethod
    async def one_or_none(self,
        query: sa.Select|str,
        values: Optional[Sequence[Mapping[str, Any]] | Mapping[str, Any]] = None,
        connection: Optional[str] = None,
        metakey: Optional[str] = None
    ) -> sa.Row|None:
        """Get one record from query.  Returns None if no record found.  Throws Exception of querying more than one record"""
        pass

    @abstractmethod
    async def scalars(self,
        query: sa.Select|str,
        values: Optional[Sequence[Mapping[str, Any]] | Mapping[str, Any]] = None,
        connection: Optional[str] = None,
        metakey: Optional[str] = None
    ) -> Sequence[Any]:
        """Get many scalar values from query.  Returns empty List if no records found. If selecting multiple columns, returns List of FIRST column only."""
        pass

    @abstractmethod
    async def scalar(self,
        query: sa.Select|str,
        values: Optional[Sequence[Mapping[str, Any]] | Mapping[str, Any]] = None,
        connection: Optional[str] = None,
        metakey: Optional[str] = None
    ) -> Any|None:
        """Get a single scalar value from query. Returns None if no record found.  Returns first (top) if more than one record found"""
        pass

    @abstractmethod
    async def scalar_one(self,
        query: sa.Select|str,
        values: Optional[Sequence[Mapping[str, Any]] | Mapping[str, Any]] = None,
        connection: Optional[str] = None,
        metakey: Optional[str] = None
    ) -> Any:
        """Get a single scalar value from query.  Throws Exception if no data found or if querying more than one record"""
        pass

    @abstractmethod
    async def scalar_one_or_none(self,
        query: sa.Select|str,
        values: Optional[Sequence[Mapping[str, Any]] | Mapping[str, Any]] = None,
        connection: Optional[str] = None,
        metakey: Optional[str] = None
    ) -> Any|None:
        """Get a single scalar value from query.  Returns None if no record found.  Throws Exception if querying more than one record"""
        pass

    @abstractmethod
    async def insertmany(self,
        query: sa.Insert|str,
        values: Optional[Sequence[Mapping[str, Any]] | Mapping[str, Any]] = None,
        connection: Optional[str] = None,
        metakey: Optional[str] = None
    ) -> List[sa.Row]:
        """Bulk insert many rows, returning bulk primary keys (for databases that support INSERT..RETURNING)"""
        pass

    @abstractmethod
    async def insertone(self,
        query: sa.Insert|str,
        values: Optional[Sequence[Mapping[str, Any]] | Mapping[str, Any]] = None,
        connection: Optional[str] = None,
        metakey: Optional[str] = None
    ) -> sa.Row:
        """Insert one row, returning the one rows PK (as a tuple in case of dual PKs)"""
        pass
