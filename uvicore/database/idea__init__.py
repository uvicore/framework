# from abc import ABC, abstractmethod

# # uvicore/
# #     foundation/
# #     database/
# #     app.py

# from uvicore import app





# ###############
# interfaces: {
#     'log': 'uvicore.log.MainLogger'
#     'log': 'mreschke.log.MyCustomLogger'

#     'db': {
#         'cli': 'uvicore.database.Database',
#         'http': 'uvicore.database.EncodeDatabase'
#     }
# }




# from uvicore import log
# log.info('hi')


# from uvicore import Database
# db = Database()


# # uvicore __init__.py
# log = import_module(interfaces['logger']).mod
# Database = import_module(interfaces['db'].mod)

# # uvicore.interfaces.__init__.py
# from .log import LogInterface


# # uvicore.interfaces.log
# class LogInterface(ABC):
#     def info(self, log):
#         pass

# from uvicore.interfaces import LogInterface
# class MainLogger(LogInterface):
#     def info(self. log):
#         print('MAIN logger info here')

# class MyCustomLogger(LogInterface):
#     def info(self, log):
#         print('MY CUSTOM logger info here')


# #contracts.py
# #from


# #from uvicore.contracts import Database
# #db = Database('constr')
# #db.select(table)
# #db.

# class DatabaseInterface(ABC):
#     """Abstract Database Interface
#     """

#     @abstractmethod
#     def example(self, something):
#         pass
