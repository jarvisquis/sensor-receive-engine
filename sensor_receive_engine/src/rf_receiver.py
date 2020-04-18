import datetime
import hashlib
import logging
import time

from redis import Redis
from rpi_rf import RFDevice
from sqlalchemy.engine import Engine

import src.models

from . import caching, parsing, persistence

logger = logging.getLogger(__name__)


class RfReceiver:
    def __init__(self, rf_device: RFDevice, db_engine: Engine, redis_conn: Redis):
        self.rf_device = rf_device
        self.ds = persistence.SensorDataStorer(db_engine)
        self.cache = caching.SensorDataCache(redis_conn)

    def start_listening(self):
        logger.info("Start listening...")
        self.rf_device.enable_rx()
        timestamp = None
        while True:
            if self.rf_device.rx_code_timestamp != timestamp:
                timestamp = self.rf_device.rx_code_timestamp
                try:
                    project_code, source_addr, nonce, data_type, data = parsing.parse_rx_code(self.rf_device.rx_code)
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
                sensor_data = src.models.SensorData.create_from_raw_data(
                    project_code, source_addr, datetime.datetime.now(), parsing.get_data_type_string(data_type), data
                )

                self.ds.save(sensor_data)
                self.cache.publish_data(sensor_data)

            time.sleep(0.1)
