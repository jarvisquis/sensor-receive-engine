import unittest
from rf_data_parse import rf_data_parse


class TestRfDataParse(unittest.TestCase):
    def test_parse_rx_code_get_nonce(self):
        rx_code = 444111245
        nonce, _, _ = rf_data_parse.parse_rx_code(rx_code)

    def test_parse_rx_code_temp(self):
        rx_code = 444111245
        _, data_type, data = rf_data_parse.parse_rx_code(rx_code)

        self.assertEqual(rf_data_parse.TEMP, data_type)
        self.assertEqual(24.5, data)

    def test_parse_rx_code_hum(self):
        rx_code = 444112080
        _, data_type, data = rf_data_parse.parse_rx_code(rx_code)

        self.assertEqual(rf_data_parse.HUM, data_type)
        self.assertEqual(8, data)

    def test_parse_rx_code_hygro(self):
        rx_code = 444113080
        _, data_type, data = rf_data_parse.parse_rx_code(rx_code)

        self.assertEqual(rf_data_parse.HYGRO, data_type)
        self.assertEqual(80, data)

    def test_parse_rx_code_error(self):
        rx_code = 444119999
        _, data_type, data = rf_data_parse.parse_rx_code(rx_code)

        self.assertEqual(rf_data_parse.ERROR, data_type)
        self.assertEqual(999, data)

    def test_parse_rx_code_throws_error_on_false_len_of_rx_code(self):
        rx_code = 1444112080
        self.assertRaises(ValueError, rf_data_parse.parse_rx_code, rx_code)

    def test_parse_rx_code_throws_error_on_false_project_code(self):
        rx_code = 244112080
        self.assertRaises(AttributeError, rf_data_parse.parse_rx_code, rx_code)

    def test_parse_rx_code_throws_error_on_unknown_data_type(self):
        rx_code = 444116080
        self.assertRaises(TypeError, rf_data_parse.parse_rx_code, rx_code)
