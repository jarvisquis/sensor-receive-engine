import logging
import subprocess
import sys
import threading
import unittest
from pathlib import Path
from time import sleep
from unittest import mock

from sensor_receive_engine.config import RedisConfig, PostgresConfig, RFConfig

sys.modules['rpi_rf'] = mock.MagicMock()
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
    @classmethod
    def setUpClass(cls) -> None:
        cls.pg_config = PostgresConfig(user='postgres',
                                       host='localhost',
                                       port=5432,
                                       database='postgres',
                                       password='test')

        cls.redis_config = RedisConfig(user='redis', host='localhost', port=6379, database=0)
        cls.rf_config = RFConfig(gpio_pin=27)
        cls.receiver = SensorDataReceiver(rf_config=cls.rf_config,
                                          db_config=cls.pg_config,
                                          redis_config=cls.redis_config)

    def test_receive_valid_message(self):
        with self.assertLogs(level=logging.DEBUG) as log_cm:
            receiver = self.receiver
            receiver.rf_device.rx_code_timestamp = None
            receiver.rf_device.enable_rx.return_value = True
            receiver.rx_code = 123

            receiver_thread = threading.Thread(target=receiver.start_listening)

            receiver_thread.start()

            receiver.rf_device.rx_code_timestamp = 1
            receiver.rf_device.rx_code = 4111123

            sleep(2)
            receiver.stop_listening()

            receiver_thread.join()
        self.assertEqual(
            log_cm.output,
            [
                "INFO:sensor_receive_engine.receiver:Start listening...",
                "DEBUG:sensor_receive_engine.receiver:Successfully received message",
                "DEBUG:sensor_receive_engine.receiver:rx_code: 4111123",
                "INFO:sensor_receive_engine.receiver:Stop Listening...",
            ],
        )

    def test_duplicate_message(self):
        with self.assertLogs(level=logging.DEBUG) as log_cm:
            receiver = self.receiver
            receiver.rf_device.rx_code_timestamp = None
            receiver.rf_device.enable_rx.return_value = True
            receiver.rx_code = 123

            receiver_thread = threading.Thread(target=receiver.start_listening)

            receiver_thread.start()

            receiver.rf_device.rx_code_timestamp = 1
            receiver.rf_device.rx_code = 4111999
            sleep(2)
            receiver.rf_device.rx_code_timestamp = 2
            receiver.rf_device.rx_code = 4111999

            sleep(2)
            receiver.stop_listening()

            receiver_thread.join()
        self.assertEqual(
            log_cm.output,
            [
                "INFO:sensor_receive_engine.receiver:Start listening...",
                "DEBUG:sensor_receive_engine.receiver:Successfully received message",
                "DEBUG:sensor_receive_engine.receiver:rx_code: 4111999",
                "DEBUG:sensor_receive_engine.receiver:Received duplicate message",
                "DEBUG:sensor_receive_engine.receiver:rx_code: 4111999",
                "INFO:sensor_receive_engine.receiver:Stop Listening...",
            ],
        )

    def test_invalidate_message(self):
        with self.assertLogs(level=logging.DEBUG) as log_cm:
            receiver = self.receiver
            receiver.rf_device.rx_code_timestamp = None
            receiver.rf_device.enable_rx.return_value = True
            receiver.rx_code = 123

            receiver_thread = threading.Thread(target=receiver.start_listening)

            receiver_thread.start()

            receiver.rf_device.rx_code_timestamp = 1
            receiver.rf_device.rx_code = 4111

            sleep(2)
            receiver.stop_listening()

            receiver_thread.join()
        self.assertEqual(
            log_cm.output,
            [
                "INFO:sensor_receive_engine.receiver:Start listening...",
                "DEBUG:sensor_receive_engine.receiver:Got wrong digit count",
                "INFO:sensor_receive_engine.receiver:Stop Listening...",
            ],
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(name)s %(levelname)s %(message)s")
    unittest.main()
