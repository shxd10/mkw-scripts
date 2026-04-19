"""
This script will not go over 15uf, and will also wheelie for you
(assuming you're in a br state, of course)
"""
from dolphin import controller, event, memory, utils # type: ignore
import Modules.mkw_classes as mkw
from Modules import mkw_utils
from Modules.macro_utils import MKWiiGCController


@event.on_frameadvance
def on_frame_advance():
    if mkw.RaceManager().state() != mkw.RaceState.RACE:
        return
    
    kart_object = mkw.KartObject(0)
    kart_move = mkw.KartMove(addr=kart_object.kart_move())
    pitch_rot = mkw_utils.get_facing_angle(0).pitch
    iv = kart_move.speed()

    ctrl = MKWiiGCController(controller)
    user_inputs = ctrl.user_inputs()
    
    if 13.8 < iv < 15.1:
        if user_inputs["A"]:
            ctrl.set_inputs({
                "A": False,
            })

    if pitch_rot < 10.0:
        ctrl.set_inputs({
            "Up": True,
        })

@event.on_savestateload
def on_state_load():
    if memory.is_memory_accessible():
        on_frame_advance()
    else:
        print("Memory not accessible.")