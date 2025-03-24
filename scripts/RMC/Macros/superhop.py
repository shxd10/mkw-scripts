"""
Usage: While script is active, commit to a drift to start superhopping in that direction.
To counterhop, hold the stick in the opposite direction of the superhopping. To wheelie between
hops, hold the UP button. Vertical stick inputs will not be overwritten.
"""
from dolphin import controller, event, gui # type: ignore
import dataclasses
import Modules.mkw_classes as mkw
from Modules.macro_utils import MKWiiGCController

@dataclasses.dataclass
class State:
    stage: int = -1
    direction: int = 0
    hold_drift: bool = False

    def __repr__(self):
        return str(self.__dict__)
    
    def copy(self):
        return State(**dataclasses.asdict(self))


S = State()
SAVESTATES = [S.copy()] * 10

TOGGLE_BUTTON = False
DEBUG_DISPLAY = False


@event.on_savestatesave
def on_save_state(is_slot: bool, slot: int):
    if is_slot:
        SAVESTATES[slot] = S.copy()

@event.on_savestateload
def on_load_state(is_slot: bool, slot: int):
    global S
    if is_slot:
        S = SAVESTATES[slot].copy()


@event.on_frameadvance
def on_frame_advance():
    global S

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
    surface_properties = kart_collide.surface_properties().value

    """
    Ideas:
    - Always drift on counterhops?
    - Hold B to drift between hops?
    - Some way to choose which hops are drift hops?
    """

    if DEBUG_DISPLAY:
        gui.draw_text((10, gui.get_display_size()[1] - 20), 0xFFFFFFFF, S.__repr__())

    # Start superhopping on first drift commit
    if S.stage == -1 and kart_move.hop_stick_x() != 0:
        S.stage = 0
        S.direction = kart_move.hop_stick_x()

    # Default superhopping state
    if S.stage == 0:
        # If vehicle is on ground, start hop sequence
        if surface_properties != 0:
            S.stage = 1
        # Otherwise, vehicle is in air so apply spindrift inputs
        else:
            neutral_glide = abs(kart_move.lean_rot()) + kart_move.lean_rot_increase() > kart_move.lean_rot_cap()
            ctrl.set_inputs({
                "A": True,
                "B": True,
                "StickX": 0 if neutral_glide else (7 * S.direction),
                "Up": False,
            })
    
    # Hop sequence, Frame 1
    if S.stage == 1:
        # If next hop is drift hop, hold drift for one more frame
        if S.hold_drift:
            ctrl.set_inputs({
                "A": True,
                "B": True,
                "StickX": 7 * S.direction,
                "Up": False,
            })
        # If next hop isn't drift hop, skip
        else:
            S.stage = 2
    # Frame 2: Release drift
    if S.stage == 2:
        ctrl.set_inputs({
            "A": True,
            "B": False,
            "StickX": 2 * S.direction,
            "Up": user_inputs["Up"],
        })
    # Frame 3: Hop
    if S.stage == 3:
        ctrl.set_inputs({
            "A": True,
            "B": True,
            "StickX": 2 * S.direction,
            "Up": False,
        })
    # Frame 4: Commit drift
    if S.stage == 4:
        ctrl.set_inputs({
            "A": True,
            "B": True,
            "StickX": (2 * S.direction) if (user_inputs["StickX"] * S.direction > 0) else (-1 * S.direction),
            "Up": False,
        })
    # Frame 5: Spindrift
    if S.stage == 5:
        ctrl.set_inputs({
            "A": True,
            "B": True,
            "StickX": 7 * S.direction,
            "Up": False,
        })
        S.hold_drift = not S.hold_drift
        S.stage = 0
    
    if S.stage > 0:
        S.stage += 1
