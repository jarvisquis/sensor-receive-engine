"""
Handles rx receiving, caching and storage
"""
import logging
import time

from redis import Redis
from sqlalchemy.engine import Engine

from . import error, parse
from .model import SensorData
from .persistence import SensorDataCache, SensorDataStorage

logger = logging.getLogger(__name__)


class SensorDataReceiver:
    def __init__(self, rf_device, db_engine: Engine, redis_conn: Redis):
        self.rf_device = rf_device
        self.data_storage = SensorDataStorage(db_engine)
        self.cache = SensorDataCache(redis_conn)
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
