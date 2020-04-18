import hashlib

from redis import Redis

from src.models import SensorData


class SensorDataCache:
    def __init__(self, redis_conn: Redis):
        self.redis_conn = redis_conn

    def cache_data(self, project_code, source_addr, nonce, data_type) -> bool:
        redis_key = self._hash_input(data_type, nonce, project_code, source_addr)
        if self.redis_conn.get(redis_key) is not None:
            self.redis_conn.setex(redis_key, 30, "")
            return False
        self.redis_conn.setex(redis_key, 30, "")
        return True

    def publish_data(self, sensor_data: SensorData):
        self.redis_conn.publish("sensor_events", sensor_data.to_json())

    @staticmethod
    def _hash_input(*args):
        hash_input = "".join(map(str, [*args])).encode("utf-8")
        return hashlib.md5(hash_input).hexdigest()
