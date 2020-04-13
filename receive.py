import configparser
import logging
import signal
import sys

import redis
from rpi_rf import RFDevice
from sqlalchemy import create_engine

from sensor_receive_engine.src import rf_receiver

logger = logging.getLogger(__name__)
GPIO_PIN = 27
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0


def setup_logger():
    logging.basicConfig(level=logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')

    sh.setFormatter(formatter)
    logger.addHandler(sh)


def on_receive_sigint(x, y):
    logger.info('Caught sigint. Stopping receive...')
    rf_device.cleanup()
    redis_conn.close()
    logger.info('Clean up complete')
    sys.exit(0)


if __name__ == '__main__':
    setup_logger()
    config = configparser.ConfigParser()
    config.read('sensor_receive_engine.conf')

    engine = create_engine(f"postgresql://{config['postgresql']['user']}:{config['postgresql']['password']}"
                           f"@{config['postgresql']['host']}:{config['postgresql']['port']}"
                           f"/{config['postgresql']['database']}")
    redis_conn = redis.Redis(host=config['redis']['host'],
                             port=config['redis']['port'],
                             db=config['redis']['database'])
    rf_device = RFDevice(config['rf']['gpio_pin'])

    rf_receiver = rf_receiver.RfReceiver(rf_device, engine, redis_conn)
    signal.signal(signal.SIGINT, on_receive_sigint)

    rf_receiver.start_listening()
