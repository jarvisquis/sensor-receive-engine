import datetime
import json
import logging
import sqlite3
from hashlib import md5

logger = logging.getLogger(__name__)

SQL_LITE_DB = 'sensor_data.db'
DATE_FORMAT_STR = "%Y%m%d%H%M%S"


class SensorData:
    def __init__(self, d_id: str, sensor_id: int, received_at: datetime.datetime, d_type: str, d_value: float):
        self.d_id = d_id
        self.sensor_id = sensor_id
        self.received_at = received_at
        self.d_type = d_type
        self.d_value = d_value

    def to_json(self):
        return f'{{' \
               f'"d_id":{str(self.d_id)},' \
               f'"sensor_id":{str(self.sensor_id)},' \
               f'"received_at":{self.received_at.strftime(DATE_FORMAT_STR)},' \
               f'"d_type":{str(self.d_type)},' \
               f'"d_value":{str(self.d_value)}' \
               f'}}'

    @classmethod
    def from_json(cls, json_str: str):
        unparsed_sensor_data = json.loads(json_str)
        return cls(d_id=unparsed_sensor_data['d_id'],
                   sensor_id=unparsed_sensor_data['sensor_id'],
                   received_at=datetime.datetime.strptime(unparsed_sensor_data['received_at'], DATE_FORMAT_STR),
                   d_type=unparsed_sensor_data['d_type'],
                   d_value=unparsed_sensor_data['d_value'])

    @classmethod
    def create_from_raw_data(cls, project_id: int, source_addr: int, received_at: datetime.datetime,
                             d_type: str, d_value: float):
        sensor_id = project_id * 10 + source_addr
        received_at = received_at
        d_type = d_type
        d_value = d_value
        d_id = md5('_'.join(
            [
                str(sensor_id),
                received_at.strftime(DATE_FORMAT_STR),
                d_type,
                str(d_value)
            ]
        ).encode('utf-8')).hexdigest()
        return cls(d_id, sensor_id, received_at, d_type, d_value)


def save(data: SensorData) -> None:
    logger.info(f'Connecting to db {SQL_LITE_DB}...')
    conn = sqlite3.connect(SQL_LITE_DB)
    try:
        with conn:
            conn.execute('''
            INSERT INTO sensor_data(
            id,
            sensor_id,
            received_at,
            d_type,
            d_value,
            )
            VALUES (?,?,?,?,?)
            ''', (data.d_id, data.sensor_id, data.received_at,
                  data.d_type, data.d_value))
    except sqlite3.Error:
        logger.exception(f'Could not save sensor data.')
    finally:
        conn.close()


def get(sensor_data_id: str):
    logger.info(f'Connecting to db {SQL_LITE_DB}...')
    conn = sqlite3.connect(SQL_LITE_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
        id,
        sensor_id,
        received_at,
        d_type,
        d_value
        FROM
        sensor_data WHERE id = ?''', (sensor_data_id,))

    sensor_data = None
    for row in cursor:
        sensor_data = SensorData(row['id'],
                                 row['sensor_id'],
                                 row['received_at'],
                                 row['d_type'],
                                 row['d_value'])
    conn.close()

    if sensor_data is None:
        logger.error(f'Could not get sensor data with id {sensor_data_id}.')
    return sensor_data
