"""
Usage: Hold UP while in a wheelie to perform perfect chain wheelies automatically.
"""
from dolphin import controller, event # type: ignore
from Modules import mkw_classes as mkw
from Modules.macro_utils import MKWiiGCController

@event.on_frameadvance
def main():
    if mkw.RaceManager().state() != mkw.RaceState.RACE:
        return

    ctrl = MKWiiGCController(controller)
    user_inputs = ctrl.user_inputs()

    if user_inputs["Up"] and mkw.KartMove.wheelie_frames() == 180:
        ctrl.set_inputs({
            "Up": False
        })
