import logging
import time

from rpi_rf import RFDevice

from rf_data_parse import rf_data_parse

logger = logging.getLogger(__name__)


class RfReceiver:
    def __init__(self, gpio_pin: int):
        self.rf_device = RFDevice(gpio_pin)
        self.timestamp = None
        self.last_nonce = -1

    def destroy(self):
        self.rf_device.cleanup()

    def start_listening(self):
        logger.info('Start listening...')
        self.rf_device.enable_rx()

        nonce = -1
        while True:
            if self.rf_device.rx_code_timestamp != self.timestamp:
                self.timestamp = self.rf_device.rx_code_timestamp
                try:
                    nonce, data_type, data = rf_data_parse.parse_rx_code(self.rf_device.rx_code)
                except AttributeError:
                    logger.exception('Got wrong project code.')
                    continue

                if nonce == self.last_nonce:
                    logger.debug('Received already duplicate message')
                    logger.debug(f'rx_code: {self.rf_device.rx_code}')
                    continue

                logger.info(f'Received data')
                logger.info(f'nonce: {nonce}')
                logger.info(f'data_type: {data_type}')
                logger.info(f'data: {data}')

            time.sleep(0.1)
