from uvicore.typing import Dict


class Redis:
    """Redis Service Provider Mixin"""

    def redis_connections(self, connections: Dict, default: str):
        self.package.redis.connections = connections
        self.package.redis.connection_default = default

