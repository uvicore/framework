import uvicore
from uvicore.support.classes import classproperty
from uvicore.contracts.job import Job as JobInterface


@uvicore.service()
class Job(JobInterface):

    @classproperty
    def name(cls):
        """Get the name of this job"""
        name = str(cls).split("'")[1]
        return name

    @classproperty
    def description(cls):
        """Get the doc description of this job"""
        return cls.__doc__

    def dispatch(self):
        """Dispatch a Job Class"""
        return uvicore.jobs.dispatch(self)

    async def dispatch_async(self):
        """Dispatch an async Job Class"""
        return await uvicore.jobs.dispatch_async(self)

    async def codispatch(self):
        """Dispatch an async Job Class"""
        return await uvicore.jobs.dispatch_async(self)
