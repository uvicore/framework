import uvicore
from typing import List
from starlette.staticfiles import StaticFiles as _Static


@uvicore.service('uvicore.http.static.StaticFiles', aliases=['StaticFiles'])
class StaticFiles(_Static):

    def __init__(self, directories: List[str]):
        super().__init__()

        # Starlette static files has a reverse winning directory order
        # In starlette the FIRST defined directory wins.  But in uvicore
        # the LAST defined provider always wins (for configs, views...)
        # So we have to reverse the list
        self.all_directories = [x for x in reversed(directories)]

    def get_directories(self, directories, packages):
        pass


# IoC Class Instance
# No because not to be used by the public
#StaticFiles: _StaticFiles = uvicore.ioc.make('StaticFiles')

# Public API for import * and doc gens
#__all__ = ['_StaticFiles']
