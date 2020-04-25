"""
Models uses for sensor engine
"""
import enum
from dataclasses import dataclass
from datetime import datetime
from hashlib import md5
from typing import Union

import ujson as json
from sqlalchemy import Column
from sqlalchemy.types import DateTime, Enum, Float, Integer, String

from . import Base


class SensorDataType(enum.Enum):
    TEMP = 1
    HUM = 2
    HYGRO = 3
    VOLT = 4
    ERROR = 9


@dataclass
class SensorRawData:
    project_code: int
    source_addr: int
    nonce: int
    data_type: SensorDataType
    data_value: Union[int, float]
    received_at: datetime = datetime.utcnow()


class SensorData(Base):
    __tablename__ = "sensor_data"
    data_id = Column(String, primary_key=True)
    sensor_id = Column(Integer)
    received_at = Column(DateTime)
    data_type = Column(Enum(SensorDataType))
    data_value = Column(Float)

    def __init__(
        self, data_id: str, sensor_id: int, received_at: datetime, data_type: SensorDataType, data_value: float
    ):
        self.data_id = data_id
        self.sensor_id = sensor_id
        self.received_at = received_at
        self.data_type = data_type
        self.data_value = data_value

    def __eq__(self, other):
        return all([self.__dict__[k] == v for k, v in other.__dict__.items() if not k.startswith("_")])

    def __repr__(self):
        return (
            f"SensorData(data_id = {self.data_id}, "
            f"sensor_id = {self.sensor_id}, "
            f"received_at = {self.received_at.__repr__()}, "
            f"data_type = {self.data_type.__repr__()}, "
            f"data_value = {self.data_value.__repr__()})"
        )

    def to_json(self):
        export = dict()
        for k, v in self.__dict__.items():
            if k.startswith("_"):
                continue
            if isinstance(v, datetime):
                export[k] = v.isoformat()
            elif isinstance(v, enum.Enum):
                export[k] = v.name
            else:
                export[k] = v
        return json.dumps(export)

    @classmethod
    def from_json(cls, json_str: str):
        unparsed_sensor_data = json.loads(json_str)
        return cls(
            data_id=unparsed_sensor_data["data_id"],
            sensor_id=unparsed_sensor_data["sensor_id"],
            received_at=datetime.fromisoformat(unparsed_sensor_data["received_at"]),
            data_type=SensorDataType[unparsed_sensor_data["data_type"]],
            data_value=unparsed_sensor_data["data_value"],
        )

    @classmethod
    def from_sensor_raw_data(cls, sensor_raw_data: SensorRawData):
        sensor_id = sensor_raw_data.project_code * 10 + sensor_raw_data.source_addr
        received_at = sensor_raw_data.received_at
        data_type = sensor_raw_data.data_type
        data_value = sensor_raw_data.data_value
        data_id = cls._build_sensor_data_id(data_type, data_value, received_at, sensor_id)
        return cls(data_id, sensor_id, received_at, data_type, data_value)

    @staticmethod
    def _build_sensor_data_id(d_type: SensorDataType, d_value: float, received_at: datetime, sensor_id: int):
        return md5(
            "_".join([str(sensor_id), received_at.isoformat(), d_type.name, str(d_value)]).encode("utf-8")
        ).hexdigest()
