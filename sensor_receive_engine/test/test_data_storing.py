import unittest
from datetime import datetime
from sensor_receive_engine.data_storing import SensorData


class TestDataStoring(unittest.TestCase):
    def test_sensor_data(self):
        project_id = 1
        source_addr = 2
        received_at = datetime(year=2020,
                               month=4,
                               day=1,
                               hour=1,
                               minute=44,
                               second=2)
        data_type = 'HUM'
        data = 12.3
        sensor_data = SensorData.create_from_raw_data(project_id,
                                                      source_addr,
                                                      received_at,
                                                      data_type,
                                                      data)

        self.assertIsInstance(sensor_data, SensorData)
