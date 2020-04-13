import datetime
import hashlib
import logging
import time

from redis import Redis
from rpi_rf import RFDevice
from sqlalchemy.engine import Engine

from sensor_receive_engine import parsing, persistence

logger = logging.getLogger(__name__)


class RfReceiver:
    def __init__(self, rf_device: RFDevice, db_engine: Engine, redis_conn: Redis):
        self.rf_device = rf_device
        self.db_engine = db_engine
        self.redis_conn = redis_conn

    def start_listening(self):
        logger.info('Start listening...')
        self.rf_device.enable_rx()
        timestamp = None
        while True:
            if self.rf_device.rx_code_timestamp != timestamp:
                timestamp = self.rf_device.rx_code_timestamp
                try:
                    project_code, source_addr, nonce, data_type, data = parsing.parse_rx_code(self.rf_device.rx_code)
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
                sensor_data = persistence.SensorData.create_from_raw_data(project_code, source_addr,
                                                                          datetime.datetime.now(),
                                                                          parsing.get_data_type_string(data_type), data)
                data_storer = persistence.SensorDataStorer(self.db_engine)
                data_storer.save(sensor_data)
                self.redis_conn.publish('sensor_events', sensor_data.to_json())

            time.sleep(0.1)
