"""
Usage: When holding left or right, neutral inputs will be added to optimize EV building via
leaning. Holding a hard direction (+-7) will turn as tight as possible without
sacrificing EV, while holding less than 7 will automatically turn as little as possible.
Can be used for neutral gliding, supersliding, or any other lean-based EV tech.
Enable this with the RFH script to perform supergrinding.
"""
from dolphin import controller, event # type: ignore
import Modules.mkw_classes as mkw
from Modules.macro_utils import MKWiiGCController

def clamp(x: int, l: int, u: int):
    return l if x < l else u if x > u else x

@event.on_frameadvance
def on_frame_advance():
    if mkw.RaceManager().state() not in (mkw.RaceState.COUNTDOWN, mkw.RaceState.RACE):
        return
    if not mkw.KartSettings.is_bike():
        return

    ctrl = MKWiiGCController(controller)
    user_inputs = ctrl.user_inputs()
    kart_move = mkw.KartMove()

    neutral_input = 1

    # Soft drift
    if abs(user_inputs['StickX']) < 7:
        ctrl.set_inputs({
            "StickX": clamp(user_inputs['StickX'], -2, 2),
        })
        neutral_input = -1

    if abs(kart_move.lean_rot()) + kart_move.lean_rot_increase() > kart_move.lean_rot_cap():
        ctrl.set_inputs({
            "StickX": neutral_input * clamp(user_inputs['StickX'], -1, 1),
        })
