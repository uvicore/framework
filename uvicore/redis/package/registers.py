from uvicore.typing import Dict


class Redis:
    """Redis Service Provider Mixin"""

    def register_redis_connections(self, connections: Dict, default: str):
        self.package.redis.connections = connections
        self.package.redis.connection_default = default

