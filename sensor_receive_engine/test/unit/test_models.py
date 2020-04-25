import unittest
from datetime import datetime

from src.model import SensorData, SensorDataType, SensorRawData


class TestSensorData(unittest.TestCase):
    def test_sensor_data(self):
        sensor_raw_data = SensorRawData(
            project_code=1,
            source_addr=2,
            received_at=datetime(year=2020, month=4, day=1, hour=1, minute=44, second=2),
            data_type=SensorDataType.HUM,
            nonce=1,
            data_value=12.3,
        )
        sensor_data = SensorData.from_sensor_raw_data(sensor_raw_data)

        self.assertIsInstance(sensor_data, SensorData)

    def test_create_from_json(self):
        json_string = (
            '{"data_id":"a28cff97edbaefeb27a3674374e8129c",'
            '"sensor_id":12,'
            '"received_at":"2020-04-01T01:44:02",'
            '"data_type":"HUM","data_value":12.3}'
        )
        sensor_data_from_json = SensorData.from_json(json_string)
        self.assertIsInstance(sensor_data_from_json, SensorData)
        self.assertEqual(
            sensor_data_from_json,
            SensorData(
                data_id="a28cff97edbaefeb27a3674374e8129c",
                sensor_id=12,
                received_at=datetime(year=2020, month=4, day=1, hour=1, minute=44, second=2),
                data_type=SensorDataType.HUM,
                data_value=12.3,
            ),
        )

    def test_to_json(self):
        expected_string = (
            '{"data_id":"a28cff97edbaefeb27a3674374e8129c",'
            '"sensor_id":12,'
            '"received_at":"2020-04-01T01:44:02",'
            '"data_type":"HUM","data_value":12.3}'
        )
        sensor_data = SensorData(
            data_id="a28cff97edbaefeb27a3674374e8129c",
            sensor_id=12,
            received_at=datetime(year=2020, month=4, day=1, hour=1, minute=44, second=2),
            data_type=SensorDataType.HUM,
            data_value=12.3,
        )
        self.assertEqual(sensor_data.to_json(), expected_string)
