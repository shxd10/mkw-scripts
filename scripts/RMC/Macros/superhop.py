"""
Usage: Hold B and commit to a drift to start superhopping in that direction. 
To counterhop, hold the stick in the opposite direction of the superhopping.
To wheelie between hops, hold the UP button. Holding R will start a normal
drift even if B is held. Vertical stick inputs will not be overwritten.
"""
from dolphin import controller, event, gui # type: ignore
import dataclasses
from Modules import mkw_classes as mkw
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
    if not mkw.KartSettings.is_bike():
        return

    ctrl = MKWiiGCController(controller)
    user_inputs = ctrl.user_inputs()

    kart_object = mkw.KartObject()
    kart_move = mkw.KartMove(addr=kart_object.kart_move())

    kart_collide = mkw.KartCollide(addr=kart_object.kart_collide())
    floor_collision = kart_collide.surface_properties().value & 0x1000 > 0

    if DEBUG_DISPLAY:
        gui.draw_text((10, gui.get_display_size()[1] - 20), 0xFFFFFFFF, state.__repr__())
    

    # Stop superhopping if R is held or B is released
    if user_inputs['R'] or not user_inputs['B']:
        state.stage = -1
        state.direction = 0
        return

    # Start superhopping on first drift commit
    if state.stage == -1 and kart_move.hop_stick_x() != 0:
        state.direction = kart_move.hop_stick_x()
        state.hold_drift = True
        state.stage = 0

    # Default superhopping state
    if state.stage == 0:
        # If vehicle is on ground, start hop sequence
        if floor_collision:
            state.stage = 1
        # Otherwise, vehicle is in air so apply spindrift inputs
        else:
            neutral_glide = abs(kart_move.lean_rot()) + kart_move.lean_rot_increase() > kart_move.lean_rot_cap()
            ctrl.set_inputs({
                "A": True,
                "B": True,
                "StickX": 0 if neutral_glide else (7 * state.direction),
                "Up": False,
            })
    
    # Hop sequence, Frame 1
    if state.stage == 1:
        # If next hop is drift hop, hold drift for one more frame
        if state.hold_drift:
            ctrl.set_inputs({
                "A": True,
                "B": True,
                "StickX": 7 * state.direction,
                "Up": False,
            })
        # If next hop isn't drift hop, skip
        else:
            state.stage = 2
    # Frame 2: Release drift
    if state.stage == 2:
        ctrl.set_inputs({
            "A": True,
            "B": False,
            "StickX": 2 * state.direction,
            "Up": user_inputs["Up"],
        })
    # Frame 3: Hop
    if state.stage == 3:
        ctrl.set_inputs({
            "A": True,
            "B": True,
            "StickX": 2 * state.direction,
            "Up": False,
        })
    # Frame 4: Commit drift
    if state.stage == 4:
        counterhop = user_inputs["StickX"] * state.direction > 0
        ctrl.set_inputs({
            "A": True,
            "B": True,
            "StickX": (2 * state.direction) if counterhop else (-1 * state.direction),
            "Up": False,
        })
    # Frame 5: Spindrift
    if state.stage == 5:
        ctrl.set_inputs({
            "A": True,
            "B": True,
            "StickX": 7 * state.direction,
            "Up": False,
        })
        state.hold_drift = not state.hold_drift
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
