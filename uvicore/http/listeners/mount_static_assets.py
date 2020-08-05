from typing import Dict, Any
from uvicore.support.dumper import dump, dd
from uvicore.events.handler import Handler


# This is just an example. this is not actually used

class MountStaticAssets(Handler):

    def handle(self, event: Dict, payload: Any):
        # self.app is available to you
        dd(event, payload.__dict__)
        dd('hindle')
