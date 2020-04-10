import datetime
import hashlib
import logging
import sys
import time

import redis
from rpi_rf import RFDevice

import sensor_receive_engine.data_storing as ds
from sensor_receive_engine.data_parsing import parse_rx_code, get_data_type_string

logger = logging.getLogger(__name__)


class RfReceiver:
    def __init__(self, gpio_pin: int):
        self.rf_device = RFDevice(gpio_pin)
        self.redis = redis.Redis(host='localhost', port='6379', db=0)

    def destroy(self):
        logger.info('Caught terminate signal')
        self.rf_device.cleanup()
        sys.exit(0)

    def start_listening(self):
        logger.info('Start listening...')
        self.rf_device.enable_rx()
        timestamp = None
        nonce = -1
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
                if self.redis.get(redis_key) is not None:
                    self.redis.setex(redis_key, 30, '')
                    logger.debug('Received duplicate message')
                    logger.debug('rx_code: {}'.format(self.rf_device.rx_code))
                    continue

                self.redis.setex(redis_key, 30, '')
                logger.debug('Successfully received message')
                logger.debug('rx_code: {}'.format(self.rf_device.rx_code))
                sensor_data = ds.SensorData.create_from_raw_data(project_code, source_addr, datetime.datetime.utcnow(),
                                                                 get_data_type_string(data_type), data)
                ds.save(sensor_data)
                self.redis.publish('sensor_events', sensor_data.to_json())

            time.sleep(0.1)
