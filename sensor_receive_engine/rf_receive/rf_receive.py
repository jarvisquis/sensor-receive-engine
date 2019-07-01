import logging
import sys
import time

from rpi_rf import RFDevice

from sensor_receive_engine.rf_data_parse import parse_rx_code, get_data_type_string

logger = logging.getLogger(__name__)


class RfReceiver:
    def __init__(self, gpio_pin: int, on_receive_callback):
        self.rf_device = RFDevice(gpio_pin)
        self.last_nonce = -1
        self.on_receive_callback = on_receive_callback

    def destroy(self):
        logger.info('Caught terminate signal')
        self.rf_device.cleanup()
        sys.exit(0)

    def start_listening(self):
        logger.info('Start listening...')
        self.rf_device.enable_rx()
        timestamp = None
        nonce = -1
        while True:
            if self.rf_device.rx_code_timestamp != timestamp:
                timestamp = self.rf_device.rx_code_timestamp
                try:
                    project_code, source_addr, nonce, data_type, data = parse_rx_code(self.rf_device.rx_code)
                except AttributeError:
                    logger.debug('Got wrong project code.')
                    continue
                except ValueError:
                    logger.debug('Got wrong digit count')
                    continue
                except TypeError:
                    logger.debug('Got wrong dtype')
                    continue

                if nonce == self.last_nonce:
                    logger.debug('Received duplicate message')
                    logger.debug('rx_code: {}'.format(self.rf_device.rx_code))
                    continue

                self.last_nonce = nonce

                logger.debug('Successfully received message')
                logger.debug('rx_code: {}'.format(self.rf_device.rx_code))
                self.on_receive_callback(project_code, source_addr, get_data_type_string(data_type), data)

            time.sleep(0.1)
