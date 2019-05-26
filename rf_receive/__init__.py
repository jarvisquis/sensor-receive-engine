from rpi_rf import RFDevice
import logging
from rf_data_parse import rf_data_parse
import time

logger = logging.getLogger(__name__)


class RfReceiver:
    def __init__(self, gpio_pin: int):
        self.rf_device = RFDevice(gpio_pin)
        self.timestamp = None

    def destroy(self):
        self.rf_device.cleanup()

    def start_listening(self):
        self.rf_device.enable_rx()
        while True:
            if self.rf_device.rx_code_timestamp != self.timestamp:
                self.timestamp = self.rf_device.rx_code_timestamp
                nonce, data_type, data = rf_data_parse.parse_rx_code(self.rf_device.rx_code)

                logger.info(f'Received data')
                logger.info(f'nonce: {nonce}')
                logger.info(f'data_type: {data_type}')
                logger.info(f'data: {data}')

            time.sleep(0.1)
