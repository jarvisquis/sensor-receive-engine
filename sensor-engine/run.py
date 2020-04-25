import logging
import signal
import sys

import dacite
import redis
import ujson as json
from rpi_rf import RFDevice
from sqlalchemy import create_engine

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
    rf_device.cleanup()
    redis_conn.close()
    logger.info("Clean up complete")
    sys.exit(0)


def _build_engine_url():
    return (
        f"postgresql://{CONFIG.postgres.user}@{CONFIG.postgres.host}:{CONFIG.postgres.port}/{CONFIG.postgres.database}"
    )


if __name__ == "__main__":
    setup_logger()
    engine = create_engine(_build_engine_url())
    redis_conn = redis.Redis(host=CONFIG.redis.host, port=CONFIG.redis.port, db=CONFIG.redis.database)
    rf_device = RFDevice(CONFIG.rf.gpio_pin)

    rf_receiver = receiver.SensorDataReceiver(rf_device, engine, redis_conn)
    signal.signal(signal.SIGINT, on_receive_sigint)

    rf_receiver.start_listening()
