import logging
import signal
import sys
from datetime import datetime
import psycopg2

from rf_receive import RfReceiver

DB_HOST = 'ccloud'
DB_DATABASE = 'sensor_data'
DB_USER = 'Sensor'
logger = logging.getLogger(__name__)


def setup_logger():
    logging.basicConfig(level=logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler(sys.stdout)
    fh = logging.FileHandler('log.txt')
    sh.setLevel(logging.INFO)
    fh.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')

    sh.setFormatter(formatter)
    fh.setFormatter(formatter)
    logger.addHandler(sh)
    logger.addHandler(fh)


def on_receive_callback(data_type: str, data):
    sql = """
        INSERT INTO env_sensor(recv_date,data_type,data_value) 
        VALUES(%s,%s,%s)
    """
    cur = db_conn.cursor()
    cur.execute(sql, (datetime.now(), data_type, float(data)))
    db_conn.commit()
    cur.close()


def on_receive_sigint(x, y):
    logger.info('Caught sigint. Stopping receive...')
    rf_receiver.destroy()
    db_conn.close()
    logger.info('Clean up complete')


if __name__ == '__main__':
    setup_logger()

    logger.info('Initiating DB connection')
    db_conn = psycopg2.connect(host=DB_HOST, database=DB_DATABASE, user=DB_USER)
    logger.info('DB connection established')

    rf_receiver = RfReceiver(27, on_receive_callback)
    signal.signal(signal.SIGINT, on_receive_sigint)
    rf_receiver.start_listening()
