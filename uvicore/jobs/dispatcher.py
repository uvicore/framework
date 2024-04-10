import uvicore
from uvicore.typing import Any
from uvicore.support.dumper import dump, dd
from uvicore.contracts import JobDispatcher as JobDispatcherInterface

@uvicore.service('uvicore.jobs.dispatcher.Dispatcher',
    aliases=['JobDispatcher'],
    singleton=True
)
class Dispatcher(JobDispatcherInterface):

    def dispatch(self, instance: object) -> Any:
        """Dispatch a Job Class"""
        return instance.handle()

    async def dispatch_async(self, instance: object) -> Any:
        return await instance.handle()

    async def codispatch(self, instance: object) -> Any:
        """Alias for dispatch_async()"""
        return await self.dispatch_async(instance)
