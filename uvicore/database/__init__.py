# type: ignore
from .db import Db
from .table import Table
from uvicore.contracts import Connection as ConnectionInterface

#from .connection import Connection
# NO, just import it to keep the same path
# Proxy instead of import to creata a nicer uvicore.database.Connection namespace
# Even if you override this the acutal class, all listings will still show this consistent namespace
#from uvicore.contracts import Connection as ConnectionInterface
# class Connection(ConnectionInterface):
#     pass

# Connection was in its own file, but I hate seeing uvicore.database.connection.Connection
# in all my dumps.  So I just added the class here directly
class Connection(ConnectionInterface):
    pass
