import uvicore
from uvicore.http import ApiRouter, Routes, ModelRouter
from uvicore.support.dumper import dump, dd


class Api(Routes[ApiRouter]):

    endpoints: str = 'app1.http.api'

    def register(self):

        # Auto API Experiment
        self.include(ModelRouter().routes())


        # Test
        #self.include('test', tags=['Test'])

        #self.include('post', tags=['Posts'])
        #self.include('user', tags=['Users'])


