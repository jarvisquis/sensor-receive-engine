import datetime
import logging
import sqlite3
from dataclasses import dataclass
from hashlib import sha256

logger = logging.getLogger(__name__)

SQL_LITE_DB = 'sensor_data.db'


@dataclass
class SensorData:
    sensor_id: str
    received_at: datetime.datetime
    sensor_type: str
    sensor_value: float
    sensor_battery_level: float

    def id(self) -> str:
        hash_input = '_'.join(list(map(str, [self.sensor_id, self.sensor_value, self.received_at]))).encode('utf-8')
        return sha256(hash_input).hexdigest()


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
            sensor_type,
            sensor_value,
            sensor_battery_level
            )
            VALUES (?,?,?,?,?)
            ''', data.id, data.sensor_id, data.received_at,
                         data.sensor_type, data.sensor_value,
                         data.sensor_battery_level)
    except sqlite3.Error as e:
        logger.exception(f'Could not save sensor data.')
    finally:
        conn.close()


def get(): ...
