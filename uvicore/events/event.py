import uvicore
from uvicore.support.dumper import dump, dd
from dataclasses import dataclass
from typing import Dict, Optional

#@dataclass
@uvicore.service()
class Event:

    def dispatch(self):
        uvicore.events._dispatch(self)

    # No, logging should be a listener
    # def log(self, cls):
    #     uvicore.log.debug("Event " + str(cls.__class__.__module__) + " Dispatched")
