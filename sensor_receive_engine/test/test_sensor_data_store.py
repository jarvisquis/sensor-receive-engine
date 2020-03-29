import unittest
from unittest.mock import patch

from sensor_receive_engine.db_communication import SensorDataStore


class TestSensorDataStore(unittest.TestCase):
    def setUp(self) -> None:
        self.host = "HOST"
        self.database = "DB"
        self.user = "USER"
        self.sensor_store = SensorDataStore(self.host, self.database, self.user)

    def test_connect(self):
        with patch('sensor_receive_engine.sensor_data_store.sensor_data_store.psycopg2.connect') as mock_conn:
            self.sensor_store._connect()

        mock_conn.assert_called_with(host=self.host, database=self.database, user=self.user)
