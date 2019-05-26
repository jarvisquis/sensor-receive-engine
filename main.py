from rf_receive import RfReceiver
import signal

if __name__ == '__name__':
    rf_receiver = RfReceiver(gpio_pin=27)
    signal.signal(signal.SIGINT, lambda x, y: rf_receiver.destroy())

    rf_receiver.start_listening()
