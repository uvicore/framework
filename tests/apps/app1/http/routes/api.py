from uvicore.http.routing import ApiRouter, Routes
from uvicore.support.dumper import dump, dd
from uvicore import app, config


class Api(Routes[ApiRouter]):

    endpoints: str = 'app1.http.api'

    def register(self):
        self.include('post', tags=['Posts'])
        self.include('user', tags=['Users'])
