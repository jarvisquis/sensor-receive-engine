import datetime
import logging
import time

from redis import Redis
from sqlalchemy.engine import Engine

from . import parse
from .model import SensorData
from .persistence import SensorDataStorage, SensorDataCache

logger = logging.getLogger(__name__)


class SensorDataReceiver:
    def __init__(self, rf_device, db_engine: Engine, redis_conn: Redis):
        self.rf_device = rf_device
        self.ds = SensorDataStorage(db_engine)
        self.cache = SensorDataCache(redis_conn)

    def start_listening(self):
        logger.info("Start listening...")
        self.rf_device.enable_rx()
        timestamp = None
        while True:
            if self.rf_device.rx_code_timestamp != timestamp:
                timestamp = self.rf_device.rx_code_timestamp
                try:
                    project_code, source_addr, nonce, data_type, data = parse.parse_rx_code(self.rf_device.rx_code)
                except AttributeError:
                    logger.debug("Got wrong project code.")
                    continue
                except ValueError:
                    logger.debug("Got wrong digit count")
                    continue
                except TypeError:
                    logger.debug("Got wrong dtype")
                    continue

                cache_result = self.cache.cache_data(project_code, source_addr, nonce, data_type)
                if not cache_result:
                    logger.debug("Received duplicate message")
                    logger.debug("rx_code: {}".format(self.rf_device.rx_code))
                    continue

                logger.debug("Successfully received message")
                logger.debug("rx_code: {}".format(self.rf_device.rx_code))
                sensor_data = SensorData.create_from_raw_data(
                    project_code, source_addr, datetime.datetime.now(), parse.get_data_type_string(data_type), data
                )

                self.ds.save(sensor_data)
                self.cache.publish_data(sensor_data)

            time.sleep(0.1)
