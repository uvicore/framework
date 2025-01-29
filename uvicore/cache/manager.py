import uvicore
from uvicore.support import module
from uvicore.typing import Dict, Any
from uvicore.support.dumper import dump, dd
from uvicore.contracts import Cache as CacheInterface


@uvicore.service('uvicore.cache.manager.Manager',
    aliases=['Cache', 'cache'],
    singleton=True,
)
class Manager:

    @property
    def default(self) -> str:
        return self._default

    @property
    def stores(self) -> Dict[str, Dict]:
        return self._stores

    @property
    def backends(self) -> Dict:
        return self._backends

    def __init__(self):
        #self.default = config.default
        #self.stores = config.stores
        self._current_store = None
        self._backends = Dict()

        # Cache app config is optional
        config = uvicore.config.app.cache.defaults({
            'default': 'array',
            'stores': {
                'redis': {
                    'driver': 'uvicore.cache.backends.redis.Redis',
                    'connection': 'cache',
                    'prefix': 'uvicore.cache::cache/',
                    'seconds': 600,
                },
                'array': {
                    'driver': 'uvicore.cache.backends.array.Array',
                    'prefix': 'uvicore.cache::cache/',
                    'seconds': 60,
                },
            }
        })
        self._default: str = config.default
        self._stores: Dict = config.stores

    def connect(self, store: str = None) -> CacheInterface:
        """Connect to a cache backend store"""
        store_name = store or self.default
        store = self.stores.get(store_name)
        if not store:
            raise Exception('Cache store {} not found'.format(store_name))

        if store_name not in self.backends:
            # Instantiate, connect and save store in local backends cache
            try:
                driver = module.load(store.driver).object(self, store)
            except ImportError:
                raise Exception(f"No library installed to handle cache store {store.driver}")

            self._backends[store_name] = driver

        return self.backends[store_name]

    def store(self, store: str = None) -> CacheInterface:
        """Alias to connect"""
        return self.connect(store)
