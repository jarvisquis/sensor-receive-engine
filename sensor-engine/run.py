import logging
import signal
import sys

import dacite
import ujson as json

from config import Configuration
from sensor_receive_engine import receiver

logger = logging.getLogger(__name__)
CONFIG = dacite.from_dict(data_class=Configuration, data=json.load("config.json"))


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
    rf_receiver.stop_listening()
    logger.info("Clean up complete")
    sys.exit(0)


if __name__ == "__main__":
    setup_logger()

    rf_receiver = receiver.SensorDataReceiver(rf_config=CONFIG.rf, db_config=CONFIG.postgres, redis_config=CONFIG.redis)
    signal.signal(signal.SIGINT, on_receive_sigint)

    rf_receiver.start_listening()
