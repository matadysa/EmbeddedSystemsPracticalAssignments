from enum import Enum, auto
from dataclasses import dataclass
import time

# code implementation explanation
# we use enum classes to make clean states
# the design choice here is so that we have just the two superstates and no off state in between
# the off state is implemented inside the heater superstate as a standby state
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

# the main state machine class
class ACStateMachine:
    # init
    def __init__(self, initial_temp: float, target_temp: float = None, cfg: ACConfig = None):
        self.cfg = cfg or ACConfig()
        self.current_temp = float(initial_temp)
        self.target_temp = float(target_temp) if target_temp is not None else float(initial_temp)

        self.superstate = None
        self.cooler_state = None
        self.heater_state = None

        self._init_state()

    # initialize the state
    def _init_state(self):
        # compute delta, delta > 0 -> heater, delta < 0 -> cooler, should be higher than hysteresis
        # if delta < hysteresis, then standby
        delta = self.target_temp - self.current_temp
        if delta < -self.cfg.hysteresis:
            self.enter_superstate(SuperState.COOLER)
            self._choose_cooler_substate(-delta)
        elif delta > self.cfg.hysteresis:
            self.enter_superstate(SuperState.HEATER)
            self._choose_heater_substate(delta)
        else:
            # neutral -> heater standby by default
            self.enter_superstate(SuperState.HEATER)
            self._set_heater_state(HeaterState.HEAT_STANDBY)

    # superstate entry/exit encapsulation
    def enter_superstate(self, s: SuperState):
        if self.superstate == s:
            return
        if self.superstate is not None:
            self._exit_superstate(self.superstate)
        self.superstate = s
        if s == SuperState.COOLER:
            self.on_enter_cooler()
        else:
            self.on_enter_heater()

    def _exit_superstate(self, s: SuperState):
        if s == SuperState.COOLER:
            self.on_exit_cooler()
        else:
            self.on_exit_heater()

    # entry/exit actions
    def on_enter_cooler(self):
        self.log("Entering COOLER superstate")
        self.heater_state = None

    def on_exit_cooler(self):
        self.log("Exiting COOLER superstate")
        self.cooler_state = None

    def on_enter_heater(self):
        self.log("Entering HEATER superstate")
        self.cooler_state = None

    def on_exit_heater(self):
        self.log("Exiting HEATER superstate")
        self.heater_state = None

    # cooler substates actions
    def _set_cooler_state(self, st: CoolerState):
        if self.cooler_state == st:
            return
        self.log(f"COOLER: {self.cooler_state} -> {st}")
        self.cooler_state = st

        if st == CoolerState.COOL_LOW:
            self._action_cool_low()
        elif st == CoolerState.COOL_MEDIUM:
            self._action_cool_medium()
        elif st == CoolerState.COOL_HIGH:
            self._action_cool_high()

    # heater substates actions
    def _set_heater_state(self, st: HeaterState):
        if self.heater_state == st:
            return
        self.log(f"HEATER: {self.heater_state} -> {st}")
        self.heater_state = st

        if st == HeaterState.HEAT_STANDBY:
            self._action_heat_standby()
        elif st == HeaterState.HEAT_PREHEAT:
            self._action_heat_preheat()
        elif st == HeaterState.HEAT_RAMP:
            self._action_heat_ramp()
        elif st == HeaterState.HEAT_MAINTAIN:
            self._action_heat_maintain()

    # machine actions
    def _action_cool_low(self):
        self.log("Action: set fan low")

    def _action_cool_medium(self):
        self.log("Action: set fan medium")

    def _action_cool_high(self):
        self.log("Action: set fan high")

    def _action_heat_standby(self):
        self.log("Action: heater standby")

    def _action_heat_preheat(self):
        self.log("Action: preheating")

    def _action_heat_ramp(self):
        self.log("Action: ramping heater power")

    def _action_heat_maintain(self):
        self.log("Action: maintaining temperature")

    # transitions
    # absolute value of delta is passed
    def _choose_cooler_substate(self, delta):
        if delta >= self.cfg.cool_high_delta:
            self._set_cooler_state(CoolerState.COOL_HIGH)
        elif delta >= self.cfg.cool_medium_delta:
            self._set_cooler_state(CoolerState.COOL_MEDIUM)
        else:
            self._set_cooler_state(CoolerState.COOL_LOW)

    def _choose_heater_substate(self, delta):
        if delta >= self.cfg.heat_ramp_delta:
            self._set_heater_state(HeaterState.HEAT_RAMP)
        elif delta >= self.cfg.heat_preheat_delta:
            self._set_heater_state(HeaterState.HEAT_PREHEAT)
        else:
            if delta > self.cfg.hysteresis:
                self._set_heater_state(HeaterState.HEAT_MAINTAIN)
            else:
                self._set_heater_state(HeaterState.HEAT_STANDBY)

    # interface
    def set_target_temperature(self, t: float):
        t = float(t)
        self.log(f"Target temperature changed {self.target_temp} -> {t}")
        self.target_temp = t

        self._evaluate()

    def temperature_update(self, current_temp: float):
        self.current_temp = float(current_temp)
        self.log(f"Temperature update: current={self.current_temp}, target={self.target_temp}")

        self._evaluate()

    # manual override for test purposes
    def manual_set(self, superstate: SuperState, substate):
        self.log(f"Manual override -> {superstate} / {substate}")
        self.enter_superstate(superstate)
        if superstate == SuperState.COOLER:
            if not isinstance(substate, CoolerState):
                raise ValueError("substate must be CoolerState for COOLER")
            self._set_cooler_state(substate)
        else:
            if not isinstance(substate, HeaterState):
                raise ValueError("substate must be HeaterState for HEATER")
            self._set_heater_state(substate)

    # logic
    def _evaluate(self):
        delta = self.target_temp - self.current_temp

        # need cooling if current > target + hysteresis
        if delta < -self.cfg.hysteresis:
            if self.superstate != SuperState.COOLER:
                self.enter_superstate(SuperState.COOLER)
            self._choose_cooler_substate(-delta)
            return
        
        # need heating if delta > hysteresis
        if delta > self.cfg.hysteresis:
            if self.superstate != SuperState.HEATER:
                self.enter_superstate(SuperState.HEATER)
            self._choose_heater_substate(delta)
            return
        
        # within hysteresis -> go to standby/maintain
        # off state is implemented as standby in heater, so we enter heater
        if self.superstate != SuperState.HEATER:
            self.enter_superstate(SuperState.HEATER)
        self._set_heater_state(HeaterState.HEAT_STANDBY)

    # helpers
    def log(self, msg: str):
        print(f"[{time.strftime('%H:%M:%S')}] {msg}")

    def status(self) -> str:
        return (f"superstate={self.superstate}, "
                f"cooler_state={self.cooler_state}, heater_state={self.heater_state}, "
                f"current_temp={self.current_temp:.2f}, target_temp={self.target_temp:.2f}")

#testing
if __name__== "__main__":
    init = float(input("Enter initial temperature: "))
    target = float(input("Enter initial target temperature: "))

    ac = ACStateMachine(initial_temp=init, target_temp=target)
    print(ac.status())

    while True:
        print("Choose an action:")
        print("1 - Update temperature")
        print("2 - Change target temperature")
        print("3 - Manual set state")
        print("4 - Show status")
        print("5 - Exit")
        choice = input("Enter choice: ")

        if choice == "1":
            temp = float(input("Enter new current temperature: "))
            ac.temperature_update(temp)
            print(ac.status())

        elif choice == "2":
            t = float(input("Enter new target temperature: "))
            ac.set_target_temperature(t)
            print(ac.status())

        elif choice == "3":
            print("Select superstate: 1=COOLER, 2=HEATER")
            s_choice = input()
            if s_choice == "1":
                print("Select cooler substate: 1=LOW, 2=MEDIUM, 3=HIGH")
                c = input()
                mapping = {"1": CoolerState.COOL_LOW, "2": CoolerState.COOL_MEDIUM, "3": CoolerState.COOL_HIGH}
                ac.manual_set(SuperState.COOLER, mapping[c])
            else:
                print("Select heater substate: 1=STANDBY, 2=PREHEAT, 3=RAMP, 4=MAINTAIN")
                h = input()
                mapping = {"1": HeaterState.HEAT_STANDBY, "2": HeaterState.HEAT_PREHEAT, "3": HeaterState.HEAT_RAMP, "4": HeaterState.HEAT_MAINTAIN}
                ac.manual_set(SuperState.HEATER, mapping[h])
            print(ac.status())

        elif choice == "4":
            print(ac.status())

        elif choice == "5":
            print("Exiting")
            break

        else:
            print("Invalid choice. Try again.")
