"""
Usage: When holding the down D-pad and committing to a direction, neutral inputs will be added to optimize EV building via
leaning. Can also be used for optimal neutral gliding.
"""
from dolphin import controller, event # type: ignore
import Modules.mkw_classes as mkw
from Modules.macro_utils import MKWiiGCController


@event.on_frameadvance
def on_frame_advance():
    if mkw.RaceManager().state() != mkw.RaceState.RACE:
        return
    if not mkw.KartSettings.is_bike():
        return

    ctrl = MKWiiGCController(controller)
    kart_move = mkw.KartMove()
    
    if ctrl.current_inputs()["Down"]:
        if abs(kart_move.lean_rot()) + kart_move.lean_rot_increase() > kart_move.lean_rot_cap():
            ctrl.set_inputs({
                "StickX": 0,
            })
