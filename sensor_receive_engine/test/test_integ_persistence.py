import subprocess
import time
import unittest
from datetime import datetime

from sqlalchemy import create_engine, text

from src.models import SensorData
from src.persistence import SensorDataStorer


class TestSensorStorer(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cmd_up = "docker-compose -f docker-compose.test.integ.persistence.yml up -d"
        subprocess.run(cmd_up.split(" "))
        print("Waiting for services to start...")
        time.sleep(5)

        cls.db_engine = create_engine("postgresql://postgres:test@localhost:5432/postgres")
        cls.sensor_data = SensorData(
            d_id="a28cff97edbaefeb27a3674374e8129c",
            sensor_id=12,
            received_at=datetime(year=2020, month=4, day=1, hour=1, minute=44, second=2),
            d_type="HUM",
            d_value=12.3,
        )

        cls.ds = SensorDataStorer(cls.db_engine)

    @classmethod
    def tearDownClass(cls) -> None:
        print("Shutting down services...")
        cmd_down = "docker-compose -f docker-compose.test.integ.persistence.yml down"
        subprocess.run(cmd_down.split(" "))

    def setUp(self) -> None:
        with self.ds.session_scope() as session:
            session.execute("TRUNCATE TABLE sensor_data")

    def test_save(self):
        save_sensor_data_id = self.sensor_data.d_id
        self.ds.save(self.sensor_data)
        sql_stmt = text("SELECT * from sensor_data where d_id = :id")
        with self.ds.session_scope() as session:
            result = session.execute(sql_stmt, {"id": save_sensor_data_id})
            for row in result:
                self.assertEqual(row["d_id"], save_sensor_data_id)

    def test_get(self):
        sql_stmt = text("INSERT INTO sensor_data VALUES (:d_id,:sensor_id,:received_at,:d_type,:d_value)")
        with self.ds.session_scope() as session:
            session.execute(sql_stmt, self.sensor_data.__dict__)

        queried_sensor_data = self.ds.get(self.sensor_data.d_id)
        self.assertIsInstance(queried_sensor_data, SensorData)
        self.assertEqual(queried_sensor_data, self.sensor_data)


if __name__ == "__main__":
    unittest.main()
