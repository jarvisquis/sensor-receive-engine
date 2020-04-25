"""
Low-level RX parsing
"""
import math
from datetime import datetime

from . import error
from .model import SensorDataType, SensorRawData


def parse_rx_code(rx_code: int,) -> SensorRawData:
    if int(math.log10(rx_code)) + 1 != 7:
        raise error.RXCodeError(f"Expected 7 digit rx_code. Got n digits: {str(int(math.log10(rx_code)) + 1)}")

    project_code = int(rx_code / 1000000)
    if project_code not in [4, 5]:
        raise error.UnknownProjectCodeError(f"Unknown project code detected. Got: {str(int(rx_code / 1000000))}")

    source_addr = int((rx_code % 1000000) / 100000)

    transmission_related_field = rx_code % 1000000 % 100000
    nonce = int(transmission_related_field / 10000)

    data_related_field = transmission_related_field % 10000
    try:
        data_type = SensorDataType(int(data_related_field / 1000))
    except ValueError:
        raise error.UnknownDataTypeError(f"Unknown data type. Got data type: {int(data_related_field / 1000)}")

    data = data_related_field % 1000

    if data_type in [SensorDataType.TEMP, SensorDataType.HUM, SensorDataType.VOLT]:
        data = data / 10

    return SensorRawData(
        project_code=project_code,
        source_addr=source_addr,
        nonce=nonce,
        data_type=data_type,
        data_value=data,
        received_at=datetime.utcnow(),
    )
