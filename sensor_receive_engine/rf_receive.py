import datetime
import hashlib
import logging
import sqlite3
import sys
import time

import redis
from rpi_rf import RFDevice

import sensor_receive_engine.data_storing as ds
from sensor_receive_engine.data_parsing import parse_rx_code, get_data_type_string

logger = logging.getLogger(__name__)
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
SQL_LITE_DB = 'sensor_data.db'


class RfReceiver:
    def __init__(self, gpio_pin: int):
        self.rf_device = RFDevice(gpio_pin)
        self.redis_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
        self.sqlite_conn = sqlite3.connect(SQL_LITE_DB)

    def destroy(self):
        logger.info('Caught terminate signal')
        self.rf_device.cleanup()
        sys.exit(0)

    def start_listening(self):
        logger.info('Start listening...')
        self.rf_device.enable_rx()
        timestamp = None
        while True:
            if self.rf_device.rx_code_timestamp != timestamp:
                timestamp = self.rf_device.rx_code_timestamp
                try:
                    project_code, source_addr, nonce, data_type, data = parse_rx_code(self.rf_device.rx_code)
                except AttributeError:
                    logger.debug('Got wrong project code.')
                    continue
                except ValueError:
                    logger.debug('Got wrong digit count')
                    continue
                except TypeError:
                    logger.debug('Got wrong dtype')
                    continue
                hash_input = ''.join(map(str, [project_code, source_addr, nonce, data_type])).encode('utf-8')
                redis_key = hashlib.md5(hash_input).hexdigest()
                if self.redis_conn.get(redis_key) is not None:
                    self.redis_conn.setex(redis_key, 30, '')
                    logger.debug('Received duplicate message')
                    logger.debug('rx_code: {}'.format(self.rf_device.rx_code))
                    continue

                self.redis_conn.setex(redis_key, 30, '')
                logger.debug('Successfully received message')
                logger.debug('rx_code: {}'.format(self.rf_device.rx_code))
                sensor_data = ds.SensorData.create_from_raw_data(project_code, source_addr, datetime.datetime.now(),
                                                                 get_data_type_string(data_type), data)
                ds.save(sensor_data, self.sqlite_conn)
                self.redis_conn.publish('sensor_events', sensor_data.to_json())

            time.sleep(0.1)
