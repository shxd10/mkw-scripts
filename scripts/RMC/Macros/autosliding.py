"""
Usage: Hold B and commit to a drift to start superhopping in that direction. 
To counterhop, hold the stick in the opposite direction of the superhopping.
To wheelie between hops, hold the UP button. Holding R will start a normal
drift even if B is held. Vertical stick inputs will not be overwritten.
"""

# The "template" for this code was mostly took from Epik's superhop macro, i just modified it to allow auto-sliding instead!

from dolphin import controller, event, gui # type: ignore
import dataclasses
import Modules.mkw_classes as mkw
from Modules.macro_utils import MKWiiGCController

DEBUG_DISPLAY = False

@dataclasses.dataclass
class State:
    stage: int = -1
    direction: int = 0
    hold_drift: bool = False

    def __repr__(self):
        return str(self.__dict__)
    
    def copy(self):
        return State(**dataclasses.asdict(self))
    

@event.on_savestatesave
def on_save_state(is_slot: bool, slot: int):
    if is_slot:
        savestates[slot] = state.copy()

@event.on_savestateload
def on_load_state(is_slot: bool, slot: int):
    global state
    if is_slot:
        state = savestates[slot].copy()


@event.on_frameadvance
def on_frame_advance():
    global state

    race_mgr = mkw.RaceManager()
    if race_mgr.state().value != mkw.RaceState.RACE.value:
        return

    ctrl = MKWiiGCController(controller)
    user_inputs = ctrl.user_inputs()

    kart_object = mkw.KartObject()
    kart_move = mkw.KartMove(addr=kart_object.kart_move())

    kart_collide = mkw.KartCollide(addr=kart_object.kart_collide())
    surface_properties = kart_collide.surface_properties().value
    
    auto_drift_counter = kart_move.auto_drift_start_frame_counter()
    analog_direction = None
    
    try:
        if user_inputs['StickX'] >= 1:
            analog_direction = 1
        elif user_inputs['StickX'] <= -1:
            analog_direction = -1
        else:
            analog_direction = 0
    except e as e:
        print(e)

    if DEBUG_DISPLAY:
        gui.draw_text((10, gui.get_display_size()[1] - 20), 0xFFFFFFFF, state.__repr__())

    # Stop autosliding if down is released
    if not user_inputs['Down']:
        state.stage = -1
        state.direction = 0
        return

    # Start stages on first direction commit
    if state.stage == -1 and analog_direction != 0:
        state.stage = 0
        state.direction = analog_direction

    # Stage 0: hold hard right/left until you complete a drift
    if state.stage == 0:
        # if vehicle did not complete an auto drift yet
        if auto_drift_counter < 11:
            ctrl.set_inputs({
                "StickX": 7 * state.direction
            })
        # else, vehicle already completed an auto drift (>12f)
        else:
            state.stage = 1
    
    # Frame 1: ±6
    if state.stage == 1:
        ctrl.set_inputs({
            "StickX": -6 * state.direction
        })
    
    # Frame 2: ±5
    if state.stage == 2:
        ctrl.set_inputs({
            "StickX": 5 * state.direction
        })
        state.stage = 0
    
    if state.stage > 0:
        state.stage += 1


def main():
    global state
    state = State()

    global savestates
    savestates = [state.copy()] * 10


if __name__ == '__main__':
    main()
