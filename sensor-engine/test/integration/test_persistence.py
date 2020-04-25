import subprocess
import time
import unittest
from datetime import datetime
from pathlib import Path

from redis import Redis
from sqlalchemy import create_engine, text

from sensor_receive_engine.model import (SensorData, SensorDataType,
                                         SensorRawData)
from sensor_receive_engine.persistence import (SensorDataCache,
                                               SensorDataStorage)

SCRIPT_DIR = Path(__file__).parent.absolute()
SERVICE_WAITING_TIME = 5


def setUpModule():
    cmd_up = f"docker-compose -f {SCRIPT_DIR}/docker-compose.yml up -d"
    subprocess.run(cmd_up.split(" "))
    print("Waiting for services to start...")
    time.sleep(SERVICE_WAITING_TIME)


def tearDownModule():
    print("Shutting down services...")
    cmd_down = f"docker-compose -f {SCRIPT_DIR}/docker-compose.yml down"
    subprocess.run(cmd_down.split(" "))


class TestSensorStorage(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.db_engine = create_engine("postgresql://postgres:test@localhost:5432/postgres")
        cls.sensor_data = SensorData(
            data_id="a28cff97edbaefeb27a3674374e8129c",
            sensor_id=12,
            received_at=datetime(year=2020, month=4, day=1, hour=1, minute=44, second=2),
            data_type=SensorDataType.HUM,
            data_value=12.3,
        )

        cls.ds = SensorDataStorage(cls.db_engine)

    def setUp(self) -> None:
        with self.ds.session_scope() as session:
            session.execute("TRUNCATE TABLE sensor_data")

    def test_save(self):
        save_sensor_data_id = self.sensor_data.data_id
        self.ds.save(self.sensor_data)
        sql_stmt = text("SELECT * from sensor_data where data_id = :id")
        with self.ds.session_scope() as session:
            result = session.execute(sql_stmt, {"id": save_sensor_data_id})
            for row in result:
                self.assertEqual(row["data_id"], save_sensor_data_id)

    def test_get(self):
        sql_stmt = text("INSERT INTO sensor_data VALUES (:data_id,:sensor_id,:received_at,'HUM',:data_value)")
        with self.ds.session_scope() as session:
            session.execute(sql_stmt, self.sensor_data.__dict__)

        queried_sensor_data = self.ds.get(self.sensor_data.data_id)
        self.assertIsInstance(queried_sensor_data, SensorData)
        self.assertEqual(queried_sensor_data, self.sensor_data)


class TestSensorCache(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.redis_conn = Redis(host="localhost", port=6379, db=0)
        cls.cache = SensorDataCache(cls.redis_conn)

    def setUp(self) -> None:
        self.redis_conn.flushdb()

    def test_cache_data(self):
        sensor_raw_data = SensorRawData(
            project_code=4, source_addr=2, nonce=1, data_type=SensorDataType.HUM, data_value=12.3
        )

        redis_key = self.cache._hash_input(
            sensor_raw_data.data_type, sensor_raw_data.nonce, sensor_raw_data.project_code, sensor_raw_data.source_addr
        )
        cache_result = self.cache.cache_data(sensor_raw_data)
        self.assertTrue(cache_result)
        self.assertIsNotNone(self.redis_conn.get(redis_key))

    def test_cache_data_duplicate(self):
        sensor_raw_data = SensorRawData(
            project_code=4, source_addr=2, nonce=1, data_type=SensorDataType.HUM, data_value=12.3
        )

        self.cache.cache_data(sensor_raw_data)
        cache_result = self.cache.cache_data(sensor_raw_data)
        self.assertFalse(cache_result)

    def test_publish_data(self):
        sensor_data = SensorData(
            data_id="a28cff97edbaefeb27a3674374e8129c",
            sensor_id=12,
            received_at=datetime(year=2020, month=4, day=1, hour=1, minute=44, second=2),
            data_type=SensorDataType.HUM,
            data_value=12.3,
        )

        ps = self.redis_conn.pubsub(ignore_subscribe_messages=True)
        ps.subscribe("sensor_events")
        ps.get_message()
        self.cache.publish_data(sensor_data)
        ps.get_message()
        result = ps.get_message()
        received_sensor_data = SensorData.from_json(result["data"].decode("utf-8"))
        self.assertEqual(received_sensor_data, sensor_data)


if __name__ == "__main__":
    unittest.main()
