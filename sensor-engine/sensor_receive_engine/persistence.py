"""
This module handles persistence of sensor data to a postgres db
"""
import hashlib
from contextlib import contextmanager
from typing import Optional

from redis import Redis
from sqlalchemy.orm import sessionmaker

from . import Base, error
from .model import SensorData, SensorRawData


class SensorDataStorage:
    def __init__(self, engine):
        Base.metadata.create_all(engine)
        self.Session = sessionmaker(bind=engine)

    def save(self, data: SensorData) -> None:
        with self.session_scope() as session:
            session.add(data)

    def get(self, sensor_data_id: str) -> Optional[SensorData]:
        with self.session_scope() as session:
            sensor_data = session.query(SensorData).filter(SensorData.data_id == sensor_data_id).first()
            session.expunge_all()

            if sensor_data is None:
                raise error.SensorDataNotFoundError(f"Could not get sensor data with id {sensor_data_id}.")
            return sensor_data

    def close(self):
        pass

    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        session = self.Session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()


class SensorDataCache:
    def __init__(self, redis_conn: Redis):
        self.redis_conn = redis_conn

    def cache_data(self, sensor_raw_data: SensorRawData) -> bool:
        redis_key = self._hash_input(
            sensor_raw_data.data_type, sensor_raw_data.nonce, sensor_raw_data.project_code, sensor_raw_data.source_addr
        )
        data_is_uniq = self.redis_conn.get(redis_key) is None
        self.redis_conn.setex(redis_key, 30, "test")
        return data_is_uniq

    def publish_data(self, sensor_data: SensorData):
        self.redis_conn.publish("sensor_events", sensor_data.to_json())

    def close(self):
        self.redis_conn.close()

    @staticmethod
    def _hash_input(*args):
        hash_input = "".join(map(str, [*args])).encode("utf-8")
        return hashlib.md5(hash_input).hexdigest()
