"""
Defines custom errors for sensor engine
"""


class SensorError(Exception):
    pass


class SensorParsingError(SensorError):
    pass


class SensorDataError(SensorError):
    pass


class RXCodeError(SensorParsingError):
    pass


class UnknownProjectCodeError(SensorParsingError):
    pass


class UnknownDataTypeError(SensorParsingError):
    pass


class SensorDataNotFoundError(SensorDataError):
    pass
