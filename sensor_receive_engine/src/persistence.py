"""
This module handles persistence of sensor data to a postgres db
"""
import hashlib
import logging
from contextlib import contextmanager
from typing import Optional

from redis import Redis
from sqlalchemy.orm import sessionmaker

from src import Base
from src.model import SensorData

logger = logging.getLogger(__name__)


class SensorDataStorage:
    def __init__(self, engine):
        Base.metadata.create_all(engine)
        self.Session = sessionmaker(bind=engine)

    def save(self, data: SensorData) -> None:
        with self.session_scope() as session:
            session.add(data)

    def get(self, sensor_data_id: str) -> Optional[SensorData]:
        with self.session_scope() as session:
            sensor_data = session.query(SensorData).filter(SensorData.d_id == sensor_data_id).first()
            session.expunge_all()

            if sensor_data is None:
                logger.error(f"Could not get sensor data with id {sensor_data_id}.")
            return sensor_data

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

    def cache_data(self, project_code, source_addr, nonce, data_type) -> bool:
        redis_key = self._hash_input(data_type, nonce, project_code, source_addr)
        data_is_uniq = self.redis_conn.get(redis_key) is None
        self.redis_conn.setex(redis_key, 30, "test")
        return data_is_uniq

    def publish_data(self, sensor_data: SensorData):
        self.redis_conn.publish("sensor_events", sensor_data.to_json())

    @staticmethod
    def _hash_input(*args):
        hash_input = "".join(map(str, [*args])).encode("utf-8")
        return hashlib.md5(hash_input).hexdigest()
