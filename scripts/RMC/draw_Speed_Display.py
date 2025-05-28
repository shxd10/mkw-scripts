from dolphin import gui, event
from Modules import input_display as display
import math

from Modules.mkw_classes import RaceManager, RaceManagerPlayer, RaceState
from Modules.mkw_classes import VehiclePhysics
from Modules import mkw_utils as mkw_utils


@event.on_frameadvance
def on_frame_advance():
    race_mgr = RaceManager()
    if race_mgr.state().value >= RaceState.COUNTDOWN.value:

        # TODO: use masks instead of the values for buttons
        race_mgr_player_addr = race_mgr.race_manager_player()
        race_mgr_player = RaceManagerPlayer(addr=race_mgr_player_addr)
        
        yaw = mkw_utils.get_facing_angle(0).yaw + 90
        IV = VehiclePhysics.internal_velocity(0)
        EV = VehiclePhysics.external_velocity(0)

        size = gui.get_display_size()
        center = (128, size[1]-128)
        

        # Yaw
        gui.draw_line(center, (center[0]+math.cos(yaw/180*math.pi)*30, center[1]+math.sin(yaw/180*math.pi)*30), 0xAAFF0000, 2)

        # IV
        gui.draw_line(center, (center[0]+IV.x, center[1]+IV.z), 0xAA00FF00, 1)

        # EV
        gui.draw_line(center, (center[0]+EV.x, center[1]+EV.z), 0xAA0000FF, 1)
          
