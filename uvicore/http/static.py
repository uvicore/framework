from typing import List

from starlette.staticfiles import StaticFiles as _StaticFiles


class StaticFiles(_StaticFiles):

    def __init__(self, directories: List[str]):
        super().__init__()

        # Starlette static files has a reverse winning directory order
        # In starlette the FIRST defined directory wins.  But in uvicore
        # the LAST defined provider always wins (for configs, views...)
        # So we have to reverse the list
        self.all_directories = [x for x in reversed(directories)]

    def get_directories(self, directories, packages):
        pass
