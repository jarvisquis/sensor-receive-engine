import logging
import signal
import sys

from sensor_receive_engine.rf_receive import RfReceiver
from sensor_receive_engine.sensor_data_store import SensorDataStore

DB_HOST = 'ccloud'
DB_DATABASE = 'sensor_data'
DB_USER = 'Sensor'
logger = logging.getLogger(__name__)


def setup_logger():
    logging.basicConfig(level=logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')

    sh.setFormatter(formatter)
    logger.addHandler(sh)


def on_receive_callback(project_code: int, source_addr: int, data_type: str, data):
    data_storer.store_sensor_values(project_code, source_addr, data_type, data)


def on_receive_sigint(x, y):
    logger.info('Caught sigint. Stopping receive...')
    rf_receiver.destroy()
    data_storer.destroy()
    logger.info('Clean up complete')


if __name__ == '__main__':
    setup_logger()
    data_storer = SensorDataStore(host=DB_HOST, database=DB_DATABASE, user=DB_USER)
    rf_receiver = RfReceiver(27, on_receive_callback)
    signal.signal(signal.SIGINT, on_receive_sigint)

    rf_receiver.start_listening()
