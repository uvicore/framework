from .table import Table
from .connection import Connection

# NO, just import it to keep the same path
# Proxy instead of import to creata a nicer uvicore.database.Connection namespace
# Even if you override this the acutal class, all listings will still show this consistent namespace
#from uvicore.contracts import Connection as ConnectionInterface
# class Connection(ConnectionInterface):
#     pass
