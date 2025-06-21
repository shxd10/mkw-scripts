"""
Usage: Hold left or right while in a wheelie to perform optimal wheelie turning. Currently
does not account for boosts.
"""
from dolphin import controller, event # type: ignore
import math
from Modules import mkw_classes as mkw
from Modules.macro_utils import MKWiiGCController

def clamp(x: int, l: int, u: int):
    return l if x < l else u if x > u else x

@event.on_frameadvance
def on_frame_advance():
    if mkw.RaceManager().state() != mkw.RaceState.RACE:
        return
    if not mkw.KartSettings.is_bike():
        return
    
    ctrl = MKWiiGCController(controller)
    user_inputs = ctrl.user_inputs()

    player_stats = mkw.PlayerStats()
    kart_move = mkw.KartMove()

    current_speed = kart_move.speed()
    top_speed = player_stats.base_speed() * 1.15
    turn_speed = player_stats.handling_speed_multiplier()
    A3 = player_stats.standard_accel_as(3)
    
    formula = math.ceil(((1 - ((top_speed - A3) / top_speed)) / (1 - turn_speed)) * 7)

    is_in_wheelie = mkw.KartState.bitfield(field_idx=0) & 0x20000000 > 0

    if is_in_wheelie:
        stick_val = 0
        if top_speed < current_speed * (turn_speed + (1 - turn_speed)) + A3:
            if formula == 1:
                stick_val = 1
            elif formula == 2:
                stick_val = 2
        else:
            if formula == 1:
                pass
            elif formula == 2:
                stick_val = 1
        
        ctrl.set_inputs({
            "StickX": clamp(user_inputs["StickX"], -stick_val, stick_val)
        })
