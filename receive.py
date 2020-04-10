import logging
import signal
import sys

from sensor_receive_engine.rf_receive import RfReceiver

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


def on_receive_sigint(x, y):
    logger.info('Caught sigint. Stopping receive...')
    rf_receiver.destroy()
    logger.info('Clean up complete')


if __name__ == '__main__':
    setup_logger()
    rf_receiver = RfReceiver(27)
    signal.signal(signal.SIGINT, on_receive_sigint)

    rf_receiver.start_listening()
