import unittest

from src import parse


class TestRfDataParse(unittest.TestCase):
    def test_parse_rx_code_return(self):
        project_code = "4"
        source_address = "2"
        nonce = "1"
        data_type = "1"
        data_value = "24.5"
        rx_code = int(project_code + source_address + nonce + data_type + data_value.replace(".", ""))
        result = parse.parse_rx_code(rx_code)
        self.assertIsInstance(result, tuple)
        self.assertEqual(5, len(result), "Expected 5 return values in tuple")
        self.assertIn(int(project_code), result)
        self.assertIn(int(source_address), result)
        self.assertIn(int(nonce), result)
        self.assertIn(int(data_type), result)
        self.assertIn(float(data_value), result)

    def test_parse_rx_code_temp(self):
        rx_code = 4111245
        _, _, _, data_type, data = parse.parse_rx_code(rx_code)

        self.assertEqual(parse.TEMP, data_type)
        self.assertEqual(24.5, data)

    def test_parse_rx_code_hum(self):
        rx_code = 4112080
        _, _, _, data_type, data = parse.parse_rx_code(rx_code)

        self.assertEqual(parse.HUM, data_type)
        self.assertEqual(8, data)

    def test_parse_rx_code_hygro(self):
        rx_code = 4113080
        _, _, _, data_type, data = parse.parse_rx_code(rx_code)

        self.assertEqual(parse.HYGRO, data_type)
        self.assertEqual(80, data)

    def test_parse_rx_code_volt(self):
        rx_code = 4114080
        _, _, _, data_type, data = parse.parse_rx_code(rx_code)

        self.assertEqual(parse.VOLT, data_type)
        self.assertEqual(8.0, data)

    def test_parse_rx_code_error(self):
        rx_code = 4119999
        _, _, _, data_type, data = parse.parse_rx_code(rx_code)

        self.assertEqual(parse.ERROR, data_type)
        self.assertEqual(999, data)

    def test_parse_rx_code_throws_error_on_false_len_of_rx_code(self):
        rx_code = 14112080
        self.assertRaises(ValueError, parse.parse_rx_code, rx_code)

    def test_parse_rx_code_throws_error_on_false_project_code(self):
        rx_codes = [1112080, 2112080, 3112080]

        for rx_code in rx_codes:
            self.assertRaises(AttributeError, parse.parse_rx_code, rx_code)

    def test_parse_rx_code_throws_error_on_unknown_data_type(self):
        rx_code = 4116080
        self.assertRaises(TypeError, parse.parse_rx_code, rx_code)
