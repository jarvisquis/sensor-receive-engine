import math

data_types = dict(
    TEMP=1,
    HUM=2,
    HYGRO=3,
    VOLTAGE=4,
    ERROR=9)


def __getattr__(name):
    if name in data_types:
        return data_types[name]


def parse_rx_code(rx_code: int):
    if int(math.log10(rx_code)) + 1 != 9:
        raise ValueError(f'Expected 9 digit rx_code. Got n digits: {int(math.log10(rx_code)) + 1}')

    project_code = int(rx_code / 1000000)
    if project_code != 444:
        raise AttributeError(f'Unknown project code detected. Got: {int(rx_code / 1000000)}')

    transmission_related_field = rx_code % 444000000 % 100000
    nonce = int(transmission_related_field / 10000)

    data_related_field = transmission_related_field % 10000
    data_type = int(data_related_field / 1000)
    if len([v for k, v in data_types.items() if v == data_type]) == 0:
        raise TypeError(f'Unknown data type. Got data type: {data_type}')

    data = data_related_field % 1000

    if data_type == data_types['TEMP'] or data_type == data_types['HUM']:
        data = data / 10

    return nonce, data_type, data
