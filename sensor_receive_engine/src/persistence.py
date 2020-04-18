"""
This module handles persistence of sensor data to a postgres db
"""
import logging
from contextlib import contextmanager
from typing import Optional

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.models import SensorData

logger = logging.getLogger(__name__)
Base = declarative_base()


class SensorDataStorer:
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
