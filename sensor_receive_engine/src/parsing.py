import math

data_types = dict(TEMP=1, HUM=2, HYGRO=3, VOLT=4, ERROR=9)


def __getattr__(name):
    if name in data_types:
        return data_types[name]


def parse_rx_code(
    rx_code: int,
) -> Tuple[
    int, int, int, int,
]:
    if int(math.log10(rx_code)) + 1 != 7:
        raise ValueError("Expected 7 digit rx_code. Got n digits:" + str(int(math.log10(rx_code)) + 1))

    project_code = int(rx_code / 1000000)
    if project_code not in [4, 5]:
        raise AttributeError("Unknown project code detected. Got:" + str(int(rx_code / 1000000)))

    source_addr = int((rx_code % 1000000) / 100000)

    transmission_related_field = rx_code % 1000000 % 100000
    nonce = int(transmission_related_field / 10000)

    data_related_field = transmission_related_field % 10000
    data_type = int(data_related_field / 1000)
    if len([v for k, v in data_types.items() if v == data_type]) == 0:
        raise TypeError("Unknown data type. Got data type:" + str(data_type))

    data = data_related_field % 1000

    if data_type in [data_types["TEMP"], data_types["HUM"], data_types["VOLT"]]:
        data = data / 10

    return project_code, source_addr, nonce, data_type, data


def get_data_type_string(data_type_int: int) -> str:
    for data_type, int_repr in data_types.items():
        if int_repr == data_type_int:
            return data_type
