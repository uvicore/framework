from uvicore.support.dumper import dump, dd
from uvicore.support.module import location
from uvicore.database import Connection
from uvicore.typing import Dict, List


class Redis:
    """Redis Service Provider Mixin"""

    def redis_connections(self, connections: Dict, default: str):
        self.package.redis.connections = connections
        self.package.redis.connection_default = default

