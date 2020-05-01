import logging
import subprocess
import threading
import unittest
from pathlib import Path
from time import sleep
from unittest import mock
import sys
from redis import Redis
from sqlalchemy import create_engine

from sensor_receive_engine.receiver import SensorDataReceiver

SCRIPT_DIR = Path(__file__).parent.absolute()
SERVICE_WAITING_TIME = 5
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


def setUpModule():
    cmd_up = f"docker-compose -f {SCRIPT_DIR}/docker-compose.yml up -d"
    subprocess.run(cmd_up.split(" "))
    print("Waiting for services to start...")
    sleep(SERVICE_WAITING_TIME)


def tearDownModule():
    print("Shutting down services...")
    cmd_down = f"docker-compose -f {SCRIPT_DIR}/docker-compose.yml down"
    subprocess.run(cmd_down.split(" "))


class TestSensorDataReceiver(unittest.TestCase):
    def test(self):
        mock_rf_device = mock.MagicMock()
        mock_rf_device.rx_code_timestamp = None
        mock_rf_device.enable_rx.return_value = True
        mock_rf_device.rx_code = 123

        db_engine = create_engine(f"postgresql://postgres:test@localhost:5432/postgres")
        redis_conn = Redis(host="localhost", port=6379, db=0)
        receiver = SensorDataReceiver(rf_device=mock_rf_device, db_engine=db_engine, redis_conn=redis_conn)
        receiver_thread = threading.Thread(target=receiver.start_listening)

        receiver_thread.start()

        sleep(2)
        mock_rf_device.rx_code_timestamp = 1
        mock_rf_device.rx_code = 4111123
        sleep(2)
        receiver.stop_listening()
        receiver_thread.join()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(name)s %(levelname)s %(message)s')
    unittest.main()
