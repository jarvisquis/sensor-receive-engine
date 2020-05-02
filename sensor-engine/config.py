"""
Configuration holder
"""
from dataclasses import dataclass

from sensor_receive_engine.config import PostgresConfig, RedisConfig, RFConfig


@dataclass
class Configuration:
    redis: RedisConfig
    postgres: PostgresConfig
    rf: RFConfig
