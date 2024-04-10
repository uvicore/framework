import uvicore
from uvicore.support.dumper import dump, dd
from dataclasses import dataclass
from uvicore.typing import Dict, Optional, Union, Callable
from uvicore.contracts.job import Job as JobInterface


@uvicore.service()
class Job(JobInterface):

    @classmethod
    @property
    def name(cls):
        """Get the name of this job"""
        name = str(cls).split("'")[1]
        return name

    @classmethod
    @property
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
