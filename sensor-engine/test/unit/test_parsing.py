import unittest

from sensor_receive_engine import error, model, parse


class TestRfDataParse(unittest.TestCase):
    def test_parse_rx_code_return(self):
        project_code = "4"
        source_address = "2"
        nonce = "1"
        data_type = "1"
        data_value = "24.5"
        rx_code = int(project_code + source_address + nonce + data_type + data_value.replace(".", ""))
        result = parse.parse_rx_code(rx_code)
        self.assertIsInstance(result, model.SensorRawData)

    def test_parse_rx_code_temp(self):
        rx_code = 4111245
        parsed = parse.parse_rx_code(rx_code)

        self.assertEqual(model.SensorDataType.TEMP, parsed.data_type)
        self.assertEqual(24.5, parsed.data_value)

    def test_parse_rx_code_hum(self):
        rx_code = 4112080
        parsed = parse.parse_rx_code(rx_code)

        self.assertEqual(model.SensorDataType.HUM, parsed.data_type)
        self.assertEqual(8, parsed.data_value)

    def test_parse_rx_code_hygro(self):
        rx_code = 4113080
        parsed = parse.parse_rx_code(rx_code)

        self.assertEqual(model.SensorDataType.HYGRO, parsed.data_type)
        self.assertEqual(80, parsed.data_value)

    def test_parse_rx_code_volt(self):
        rx_code = 4114080
        parsed = parse.parse_rx_code(rx_code)

        self.assertEqual(model.SensorDataType.VOLT, parsed.data_type)
        self.assertEqual(8.0, parsed.data_value)

    def test_parse_rx_code_error(self):
        rx_code = 4119999
        parsed = parse.parse_rx_code(rx_code)

        self.assertEqual(model.SensorDataType.ERROR, parsed.data_type)
        self.assertEqual(999, parsed.data_value)

    def test_parse_rx_code_throws_error_on_false_len_of_rx_code(self):
        rx_code = 14112080
        self.assertRaises(error.RXCodeError, parse.parse_rx_code, rx_code)

    def test_parse_rx_code_throws_error_on_false_project_code(self):
        rx_codes = [1112080, 2112080, 3112080]

        for rx_code in rx_codes:
            self.assertRaises(error.UnknownProjectCodeError, parse.parse_rx_code, rx_code)

    def test_parse_rx_code_throws_error_on_unknown_data_type(self):
        rx_code = 4116080
        self.assertRaises(error.UnknownDataTypeError, parse.parse_rx_code, rx_code)
