import unittest
from datetime import datetime
from sensor_receive_engine.data_storing import SensorData
from unittest import mock


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

    def test_create_from_json(self):
        json_string = '{"d_id":"a28cff97edbaefeb27a3674374e8129c",' \
                      '"sensor_id":12,' \
                      '"received_at":"2020-04-01T01:44:02",' \
                      '"d_type":"HUM","d_value":12.3}'
        sensor_data_from_json = SensorData.create_from_json(json_string)
        self.assertIsInstance(sensor_data_from_json, SensorData)

    def test_to_json(self):
        expected_string = '{"d_id":"a28cff97edbaefeb27a3674374e8129c",' \
                          '"sensor_id":12,' \
                          '"received_at":"2020-04-01T01:44:02",' \
                          '"d_type":"HUM","d_value":12.3}'
        sensor_data = SensorData(d_id="a28cff97edbaefeb27a3674374e8129c",
                                 sensor_id=12,
                                 received_at=datetime(year=2020,
                                                      month=4,
                                                      day=1,
                                                      hour=1,
                                                      minute=44,
                                                      second=2),
                                 d_type="HUM",
                                 d_value=12.3)
        self.assertEqual(sensor_data.to_json(), expected_string)
