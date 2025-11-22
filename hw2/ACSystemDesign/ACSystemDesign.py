from enum import Enum, auto
from dataclasses import dataclass

# code implementation explanation 
# we use enum classes to make clean states
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

# this class is added to clarify the thresholds of changing states
# hysteresis is added to avoid the system changing state because of little change in temperature
@dataclass
class ACConfig:
    cool_high_delta: float = 4.0
    cool_medium_delta: float = 2.0
    heat_preheat_delta: float = 1.0
    heat_ramp_delta: float = 3.0
    hysteresis: float = 0.3

