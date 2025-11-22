from enum import Enum, auto

class SuperState(Enum):
    COOLER = auto()
    HEATER = auto()


class CoolerState(Enum):
    COOL_LOW = auto()
    COOL_MEDIUM = auto()
    COOL_HIGH = auto()


class HeaterState(Enum):
    HEAT_STANDBY = auto()
    HEAT_PREHEAT = auto()
    HEAT_RAMP = auto()
    HEAT_MAINTAIN = auto()