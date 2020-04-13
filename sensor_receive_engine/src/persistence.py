import logging
from contextlib import contextmanager
from datetime import datetime
from hashlib import md5
from typing import Optional

import ujson as json
from sqlalchemy import Column, String, DateTime, Integer, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)
Base = declarative_base()


class SensorData(Base):
    __tablename__ = 'sensor_data'
    d_id = Column(String, primary_key=True)
    sensor_id = Column(Integer)
    received_at = Column(DateTime)
    d_type = Column(String)
    d_value = Column(Float)

    def __init__(self, d_id: str, sensor_id: int, received_at: datetime, d_type: str, d_value: float):
        self.d_id = d_id
        self.sensor_id = sensor_id
        self.received_at = received_at
        self.d_type = d_type
        self.d_value = d_value

    def __eq__(self, other):
        return other.d_id == self.d_id

    def to_json(self):
        return f'{{' \
               f'"d_id":"{str(self.d_id)}",' \
               f'"sensor_id":{str(self.sensor_id)},' \
               f'"received_at":"{self.received_at.isoformat()}",' \
               f'"d_type":"{str(self.d_type)}",' \
               f'"d_value":{str(self.d_value)}' \
               f'}}'

    @classmethod
    def create_from_json(cls, json_str: str):
        unparsed_sensor_data = json.loads(json_str)
        return cls(d_id=unparsed_sensor_data['d_id'],
                   sensor_id=unparsed_sensor_data['sensor_id'],
                   received_at=datetime.fromisoformat(unparsed_sensor_data['received_at']),
                   d_type=unparsed_sensor_data['d_type'],
                   d_value=unparsed_sensor_data['d_value'])

    @classmethod
    def create_from_raw_data(cls, project_id: int, source_addr: int, received_at: datetime,
                             d_type: str, d_value: float):
        sensor_id = project_id * 10 + source_addr
        received_at = received_at
        d_type = d_type
        d_value = d_value
        d_id = cls._build_sensor_data_id(d_type, d_value, received_at, sensor_id)
        return cls(d_id, sensor_id, received_at, d_type, d_value)

    @staticmethod
    def _build_sensor_data_id(d_type: str, d_value: float, received_at: datetime, sensor_id: int):
        return md5('_'.join(
            [
                str(sensor_id),
                received_at.isoformat(),
                d_type,
                str(d_value)
            ]
        ).encode('utf-8')).hexdigest()


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
                logger.error(f'Could not get sensor data with id {sensor_data_id}.')
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
