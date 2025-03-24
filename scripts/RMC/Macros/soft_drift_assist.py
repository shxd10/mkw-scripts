"""
Usage: Hold a nonzero vertical stick input to clamp any horizontal stick inputs to optimal
soft drift values. Useful for soft drifting without turning off Full Input Range.
"""
from dolphin import controller, event # type: ignore
import Modules.mkw_classes as mkw
from Modules.macro_utils import MKWiiGCController

def clamp(x: int, l: int, u: int):
    return l if x < l else u if x > u else x

@event.on_frameadvance
def on_frame_advance():
    if mkw.RaceManager().state() != mkw.RaceState.RACE:
        return

    ctrl = MKWiiGCController(controller)
    user_inputs = ctrl.user_inputs()

    if user_inputs["StickY"] != 0:
        ctrl.set_inputs({
            "StickX": clamp(user_inputs["StickX"], -3, 3)
        })
