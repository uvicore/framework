# Database Development Readme

This is the Uvicore `database` module which bootstraps all database connections from all package configs.  It also provides a custom uvicore specific query builder on top of SQLAlchemy Core.  This query builder can be used by the end user and is also the base for the `orm` abstraction.




# Try lazy connections again?

SA Docs - The Engine, when first returned by create_engine(), has not actually tried to connect to the database yet; that happens only the first time it is asked to perform a task against the database. This is a software design pattern known as lazy initialization.
I connect in provider on Startup Event, maybe I should re-rest with 2.0?
    Have to pound it hard with wrk to be sure



# SQL to logs

Try out `create_engine.echo` boolean, should log all SQL to logger?

# UPDATES 0.2 to 0.3 docs

- deprecated db.connect(), db.disconnect(), db.databases() db.database()
- db.execute() now returns a sa.CursorResult
    - To get single inserted PK - result.inserted_primary_key
    - To get bulk inserted PK lists (not supported by MySQL) - result.inserted_primary_key_rows
- Getting columns from query results changed from results[0].keys() to results[0]._mapping.keys()
- All sa.select() does not use [] anymore, but infinite args


# Python 3.11+

all @abstractproperty

change to
    @property
    @abstractmethod


deprecated
@abstractclassmethod

change to

@classmethod
@abstractmethod

