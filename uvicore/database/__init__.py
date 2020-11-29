from uvicore.contracts import Connection as ConnectionInterface

class Connection(ConnectionInterface):
    pass

# Most do work without issue, but most are never accessed by public except
# from uvicore.database.table import Schema - But I like that path already


# This one is used publically, kind of, its displayed as the data object path in showing connections
#from .connection import Connection



