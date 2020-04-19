import configparser
import logging
import signal
import sys

import redis
from rpi_rf import RFDevice
from sqlalchemy import create_engine

from src import receiver

logger = logging.getLogger(__name__)
CONFIG = configparser.ConfigParser()
CONFIG.read("sensor_receive_engine.conf")


def setup_logger():
    logging.basicConfig(level=logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s %(name)-12s %(levelname)-8s %(message)s")

    sh.setFormatter(formatter)
    logger.addHandler(sh)


def on_receive_sigint(x, y):
    logger.info("Caught sigint. Stopping receive...")
    rf_device.cleanup()
    redis_conn.close()
    logger.info("Clean up complete")
    sys.exit(0)


if __name__ == "__main__":
    setup_logger()

    engine = create_engine(
        f"postgresql://{CONFIG['postgresql']['user']}:{CONFIG['postgresql']['password']}"
        f"@{CONFIG['postgresql']['host']}:{CONFIG['postgresql']['port']}"
        f"/{CONFIG['postgresql']['database']}"
    )
    redis_conn = redis.Redis(host=CONFIG["redis"]["host"], port=CONFIG["redis"]["port"], db=CONFIG["redis"]["database"])
    rf_device = RFDevice(CONFIG["rf"]["gpio_pin"])

    rf_receiver = receiver.SensorDataReceiver(rf_device, engine, redis_conn)
    signal.signal(signal.SIGINT, on_receive_sigint)

    rf_receiver.start_listening()
