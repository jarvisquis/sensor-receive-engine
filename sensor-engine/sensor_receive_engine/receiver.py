"""
Handles rx receiving, caching and storage
"""
import logging
import time

import rpi_rf
from redis import Redis
from sqlalchemy.engine import create_engine

from . import error, parse
from .config import PostgresConfig, RedisConfig, RFConfig
from .model import SensorData
from .persistence import SensorDataCache, SensorDataStorage

logger = logging.getLogger(__name__)


class SensorDataReceiver:
    def __init__(self, rf_config: RFConfig, db_config: PostgresConfig, redis_config: RedisConfig):
        self.rf_device = rpi_rf.RFDevice(gpio=rf_config.gpio_pin)
        self.data_storage = SensorDataStorage(create_engine(db_config.engine_url))
        self.cache = SensorDataCache(Redis(host=redis_config.host, port=redis_config.port, db=redis_config.database))
        self.shutdown_wanted = False

    def start_listening(self):
        logger.info("Start listening...")
        self.rf_device.enable_rx()
        timestamp = None
        self.shutdown_wanted = False
        while not self.shutdown_wanted:
            if self.rf_device.rx_code_timestamp != timestamp:
                timestamp = self.rf_device.rx_code_timestamp
                try:
                    sensor_raw_data = parse.parse_rx_code(self.rf_device.rx_code)
                except error.UnknownProjectCodeError:
                    logger.exception("Got wrong project code.")
                    continue
                except error.RXCodeError:
                    logger.exception("Got wrong digit count")
                    continue
                except error.UnknownDataTypeError:
                    logger.exception("Got wrong dtype")
                    continue

                cache_result = self.cache.cache_data(sensor_raw_data)
                if not cache_result:
                    logger.debug("Received duplicate message")
                    logger.debug(f"rx_code: {self.rf_device.rx_code}")
                    continue

                logger.debug("Successfully received message")
                logger.debug(f"rx_code: {self.rf_device.rx_code}")
                sensor_data = SensorData.from_sensor_raw_data(sensor_raw_data)

                self.data_storage.save(sensor_data)
                self.cache.publish_data(sensor_data)

            time.sleep(0.1)

    def stop_listening(self):
        logger.info("Stop Listening...")
        self.shutdown_wanted = True
        self.rf_device.cleanup()
        self.data_storage.close()
        self.cache.close()
