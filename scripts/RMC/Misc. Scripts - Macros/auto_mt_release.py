from dolphin import controller, event # type: ignore
import Modules.mkw_classes as mkw
from Modules.macro_utils import MKWiiGCController

release_drift = False

# @event.on_savestateload
# def on_state_load(fromSlot: bool, slot: int):
#     global release_drift
#     release_drift = False

@event.on_frameadvance
def on_frame_advance():
    global release_drift
    if mkw.RaceManager().state() != mkw.RaceState.RACE:
        return

    ctrl = MKWiiGCController(controller)
    user_inputs = ctrl.user_inputs()

    kart_move = mkw.KartMove()

    if not release_drift and (kart_move.mt_charge() == 270 or kart_move.ssmt_charge() == 75):
        release_drift = True

    elif release_drift and (user_inputs["B"] or user_inputs["R"]):
        ctrl.set_inputs({
            "B": False,
            "R": False,
        })
    
    elif release_drift:
        release_drift = False
