import subprocess
import time
import unittest
from datetime import datetime

from redis import Redis

from src.caching import SensorDataCache
from src.models import SensorData


class TestSensorCache(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cmd_up = "docker-compose -f docker-compose.yml up -d redis"
        subprocess.run(cmd_up.split(" "))
        print("Waiting for services to start...")
        time.sleep(5)

        cls.redis_conn = Redis(host="localhost", port=6379, db=0)
        cls.cache = SensorDataCache(cls.redis_conn)

    @classmethod
    def tearDownClass(cls) -> None:
        print("Shutting down services...")
        cmd_down = "docker-compose -f docker-compose.yml down"
        subprocess.run(cmd_down.split(" "))

    def setUp(self) -> None:
        self.redis_conn.flushdb()

    def test_cache_data(self):
        project_code = 4
        source_address = 2
        nonce = 1
        data_type = 1

        redis_key = self.cache._hash_input(data_type, nonce, project_code, source_address)
        cache_result = self.cache.cache_data(project_code, source_address, nonce, data_type)
        self.assertTrue(cache_result)
        self.assertIsNotNone(self.redis_conn.get(redis_key))

    def test_cache_data_duplicate(self):
        project_code = 4
        source_address = 2
        nonce = 1
        data_type = 1

        self.cache.cache_data(project_code, source_address, nonce, data_type)
        cache_result = self.cache.cache_data(project_code, source_address, nonce, data_type)
        self.assertFalse(cache_result)

    def test_publish_data(self):
        sensor_data = SensorData(
            d_id="a28cff97edbaefeb27a3674374e8129c",
            sensor_id=12,
            received_at=datetime(year=2020, month=4, day=1, hour=1, minute=44, second=2),
            d_type="HUM",
            d_value=12.3,
        )

        ps = self.redis_conn.pubsub(ignore_subscribe_messages=True)
        ps.subscribe("sensor_events")
        ps.get_message()
        self.cache.publish_data(sensor_data)
        ps.get_message()
        result = ps.get_message()
        received_sensor_data = SensorData.create_from_json(result["data"].decode("utf-8"))
        self.assertEqual(received_sensor_data, sensor_data)


if __name__ == "__main__":
    unittest.main()
