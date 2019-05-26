import unittest
from rf_receive import rf_receive


class TestRfReceive(unittest.TestCase):
    def test_parse_rx_code_get_nonce(self):
        rx_code = 444111245
        nonce, _, _ = rf_receive.parse_rx_code(rx_code)

    def test_parse_rx_code_temp(self):
        rx_code = 444111245
        _, data_type, data = rf_receive.parse_rx_code(rx_code)

        self.assertEqual(rf_receive.TEMP, data_type)
        self.assertEqual(24.5, data)

    def test_parse_rx_code_hum(self):
        rx_code = 444112080
        _, data_type, data = rf_receive.parse_rx_code(rx_code)

        self.assertEqual(rf_receive.HUM, data_type)
        self.assertEqual(8, data)

    def test_parse_rx_code_hygro(self):
        rx_code = 444113080
        _, data_type, data = rf_receive.parse_rx_code(rx_code)

        self.assertEqual(rf_receive.HYGRO, data_type)
        self.assertEqual(80, data)

    def test_parse_rx_code_error(self):
        rx_code = 444119999
        _, data_type, data = rf_receive.parse_rx_code(rx_code)

        self.assertEqual(rf_receive.ERROR, data_type)
        self.assertEqual(999, data)

    def test_parse_rx_code_throws_error_on_false_len_of_rx_code(self):
        rx_code = 1444112080
        self.assertRaises(ValueError, rf_receive.parse_rx_code, rx_code)

    def test_parse_rx_code_throws_error_on_false_project_code(self):
        rx_code = 244112080
        self.assertRaises(AttributeError, rf_receive.parse_rx_code, rx_code)

    def test_parse_rx_code_throws_error_on_unknown_data_type(self):
        rx_code = 444116080
        self.assertRaises(TypeError, rf_receive.parse_rx_code, rx_code)
