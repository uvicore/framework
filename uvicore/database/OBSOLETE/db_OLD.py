from uvicore import app
import typing
from databases import DatabaseURL
from sqlalchemy import create_engine
from typing import List, Mapping, TypeVar

E = TypeVar('E')

class Database:

    def __init__(self, url: str):
        #self.url = DatabaseURL(url)
        self.url = url
        if app.is_async:
            from databases import Database as EncodeDatabase
            # NO +pymysql
            self.encodedb = EncodeDatabase("mysql://root:techie@127.0.0.1/uvicore_wiki")
            @app.http.on_event("startup")
            async def startup():
                await self.encodedb.connect()

            @app.http.on_event("shutdown")
            async def shutdown():
                await self.encodedb.disconnect()
        else:

            self.engine = create_engine(self.url, echo=True)

        from sqlalchemy import MetaData
        self.metadata = MetaData()

    def connect(self):
        return self.engine.connect()

    def fetchone(self, entity: E, query) -> E:
        if app.is_async:
            return self.encodedb.fetch_one(query=query)
        else:
            with self.connect() as con:
                results = con.execute(query)
                return entity(**results.fetchone())

    def fetchall(self, entity, query) -> List[E]:
        if app.is_async:
            return self.encodedb.fetch_all(query=query)
        else:
            with self.connect() as con:
                results = con.execute(query)
                rows = []
                for row in results:
                    #rows.append(entity.User(**row))
                    rows.append(entity(**row))
                return rows

