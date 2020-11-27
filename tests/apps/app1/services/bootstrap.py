import uvicore
from uvicore.configuration import Env
from uvicore.support import path
from uvicore.support.dumper import dd, dump

def application(is_console: bool = False) -> None:
    """Bootstrap the application either from the CLI or Web entry points

    Bootstrap only runs when this package is running as the main app via
    ./uvicore or uvicorn/gunicorn server
    """

    # Base path
    base_path = path.find_base(__file__) + '/testapp/app'

    # Load .env from environs - NO, not for this test environment
    # NO - Env().read_env(base_path + '/.env')

    # Import this apps config (import must be after Env())
    from ..config.app import config as app_config

    # Bootstrap the Uvicore Application (Either CLI or HTTP entry points based on is_console)
    uvicore.bootstrap(app_config, base_path, is_console)

    # Return application
    return uvicore.app






















# This was my custom importer test

# def application(is_console: bool = False) -> None:
#     """Bootstrap the application either from the CLI or Web entry points

#     Bootstrap only runs when this package is running as the main app via
#     ./uvicore or uvicorn/gunicorn server
#     """

#     # Import this apps config (import must be after Env())
#     from ..config.app import config as app_config


#     bindings = {
#         # Testing, override Users table and model
#         'uvicore.auth.database.tables.users': 'app1.database.tables.users',
#         'uvicore.auth.models.user': 'app1.models.user',
#     }

#     import sys
#     import os
#     import importlib
#     from uvicore.support.dumper import dd, dump
#     from uvicore.support.module import load

#     class UvicoreLoader:
#         def __init__(self, override):
#             self.override = override

#         def load_module(self, fullname):
#             # original_meta_path = sys.meta_path

#             # if fullname + '_BASE' not in sys.modules:
#             #     new_meta_path = []
#             #     for mp in sys.meta_path:
#             #         if 'UvicoreFinder' not in str(mp):
#             #             new_meta_path.append(mp)
#             #     sys.meta_path = new_meta_path

#             #     #__import__(fullname)
#             #     load(fullname)
#             #     sys.modules[fullname + '_BASE'] = sys.modules.pop(fullname)
#             #     #dump(sys.modules.get('uvicore.auth.models.user'))


#             # orig = bindings.get(fullname)
#             # del bindings[fullname]
#             # #load(fullname)
#             # dump("IMPORTING", fullname)
#             # __import__(fullname)
#             # sys.modules[fullname + '_BASE'] = sys.modules.pop(fullname)
#             # dump('xx', sys.modules[fullname + '_BASE'])
#             # bindings[fullname] = orig

#             if '_BASE' in fullname:
#                 name = fullname[0: -5]

#                 orig = None
#                 if name in sys.modules:
#                     orig = sys.modules[name]
#                     del sys.modules[name]

#                 origb = bindings.get(name)
#                 del bindings[name]

#                 __import__(name)
#                 sys.modules[name + '_BASE'] = sys.modules.pop(name)
#                 if orig:
#                     dump('yes')
#                     sys.modules[name] = orig

#                 bindings[name] = origb

#                 return sys.modules[name + '_BASE']

#                 #dd(sys.modules)
#                 #dd(name)



#             # dump("OVERRIDE: ", self.override)
#             # if self.override in sys.modules:
#             #     dump(sys.modules.get(self.override))
#             #     return sys.modules[self.override]

#             #sys.meta_path = original_meta_path

#             #dump(sys.meta_path)
#             #dump(sys.modules)

#             #dump(self.override)
#             __import__(self.override)
#             #load(self.override)
#             mod = sys.modules[self.override]
#             #sys.modules[self.override] = mod
#             sys.modules[fullname] = mod


#             return mod

#             # fls = ["%s.py", "%s/__init__.py", "%s/"]
#             # dirpath = "/".join(self.override.split("."))
#             # for path in sys.path:
#             #     path = os.path.abspath(path)
#             #     for fp in fls:
#             #         composed_path = fp % ("%s/%s" % (path, dirpath))
#             #         if os.path.exists(composed_path):
#             #             dump("IMPORTING", composed_path)
#             #             spec = importlib.util.spec_from_file_location(self.override, composed_path)
#             #             mod = importlib.util.module_from_spec(spec)
#             #             spec.loader.exec_module(mod)
#             #             sys.modules[fullname] = mod
#             #             dump(mod)
#             #             return mod





#             # if fullname in sys.modules:
#             #     return

#             # for path in sys.path:
#             #     path = os.path.abspath(path)
#             #     fullpath = path + '/' + self.fullname
#             #     if os.path.exists(fullpath):
#             #         return fullpath
#             #     #print(path, self.fullname)



#     class UvicoreFinder:
#         def find_module(self, fullname, path=None):
#             # if '.BASE' in fullname:
#             #     fullname = fullname[0:-5]
#             #     #dump(fullname, 'x')
#             #     return UvicoreLoader2(fullname)

#             if '_BASE' in fullname:
#                 return UvicoreLoader(fullname)

#             override = bindings.get(fullname)
#             if override:
#                 #dump(sys.modules)
#                 print('override', fullname, 'with', override)
#                 return UvicoreLoader(override)
#                 #print(path)
#                 #return importlib.machinery.SourcelessFileLoader(override, path)

#                 #__import__(override)
#                 #sys.modules[fullname] = sys.modules[override]
#                 #return None


#     #sys.meta_path.insert(0, UvicoreFinder())
#     #sys.meta_path.append(UvicoreFinder())



#     # print(sys.meta_path)



#     import uvicore
#     from uvicore.configuration import Env
#     from uvicore.support import path
#     from uvicore.support.dumper import dd, dump




#     # Base path
#     base_path = path.find_base(__file__) + '/testapp/app'

#     # Load .env from environs - NO, not for this test environment
#     # NO - Env().read_env(base_path + '/.env')


#     # Bootstrap the Uvicore Application (Either CLI or HTTP entry points based on is_console)
#     uvicore.bootstrap(app_config, base_path, is_console)

#     # Return application
#     return uvicore.app
