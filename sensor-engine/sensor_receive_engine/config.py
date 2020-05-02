from dataclasses import dataclass
from typing import Optional


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
    password: Optional[str]

    @property
    def engine_url(self) -> str:
        if self.password is not None:
            return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        return f"postgresql://{self.user}@{self.host}:{self.port}/{self.database}"


@dataclass
class RFConfig:
    gpio_pin: int
