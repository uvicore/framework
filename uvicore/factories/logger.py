import uvicore
from uvicore.support.dumper import dump, dd
from uvicore.contracts import Logger as LoggerInterface

class Logger:

    def make(self, Logger: LoggerInterface):
        config = uvicore.config('app.logger')
        return Logger(config)
