"""
Configuration holder
"""
from dataclasses import dataclass


@dataclass
class RedisConfig:
    user: str
    host: str
    port: int
    database: int


@dataclass
class PostgresConfig:
    user: str
    host: str
    port: int
    database: str


@dataclass
class RFConfig:
    gpio_pin: int


@dataclass
class Configuration:
    redis: RedisConfig
    postgres: PostgresConfig
    rf: RFConfig
