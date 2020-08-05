from typing import Dict, Any
from uvicore.contracts import Dispatcher
from uvicore.support.dumper import dump, dd

class HttpEventSubscription:

    def booted(self, event: Dict, payload: Any):
        dd(event, payload.__dict__)
        dd('booted now')



    def subscribe(self, events: Dispatcher):
        events.listen('uvicore.foundation.events.app.Booted', self.booted)
