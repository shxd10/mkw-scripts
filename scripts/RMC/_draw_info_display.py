from dolphin import event, gui, utils, memory
import configparser
import math
import os

from Modules.mkw_classes.common import SurfaceProperties, eulerAngle
from Modules.mkw_utils import History 

from external.external_utils import run_external_script
from Modules import settings_utils as setting
from Modules import mkw_utils as mkw_utils
from Modules.infodisplay_utils import draw_infodisplay, create_infodisplay
from Modules.mkw_classes import RaceManager, RaceManagerPlayer, RaceState, KartObjectManager, VehiclePhysics






@event.on_savestateload
def on_state_load(fromSlot: bool, slot: int):
    global c
    c = setting.get_infodisplay_config()

    RaceComp_History.clear()
    Angle_History.clear()
    Pos_History.clear()

    global maxLap
    maxLap = 0

    global text
    if memory.is_memory_accessible() and mkw_utils.extended_race_state() >= 0:
        Angle_History.update()
        RaceComp_History.update()
        maxLap = int(RaceManagerPlayer.race_completion_max(0))
        text = create_infodisplay(c, RaceComp_History, Angle_History)
    else:
        text = ''
        


@event.on_framepresent
def on_present():
    gui.draw_text((10, 10), c.color, text)
    
    
def main():
    global c
    c = setting.get_infodisplay_config()

    global Frame_of_input
    Frame_of_input = 0

    def prc():
        if KartObjectManager.player_count() > 0:
            return RaceManagerPlayer(0).race_completion()
        return 0
    def grc():
        if KartObjectManager.player_count() > 1:
            return RaceManagerPlayer(1).race_completion()
        return 0
    def fa():
        return mkw_utils.get_facing_angle(0)
    def ma():
        return mkw_utils.get_moving_angle(0)
    def pos_():
        if KartObjectManager.player_count() > 0:
            return VehiclePhysics.position(0)
        return None
    
    global RaceComp_History
    RaceComp_History = History({'prc':prc, 'grc':grc}, c.history_size)

    global Angle_History
    Angle_History = History({'facing' : fa, 'moving' : ma}, 2)

    global Pos_History
    Pos_History = History({'pos' : pos_}, 3)

    global maxLap
    maxLap = None

    global text
    text = ''


if __name__ == '__main__':
    main()


@event.on_frameadvance
def on_frame_advance():
    global Frame_of_input
    global Angle_History
    global RaceComp_History
    global c
    global maxLap
    global text

    race_mgr = RaceManager()
    newframe = Frame_of_input != mkw_utils.frame_of_input()
    draw = mkw_utils.extended_race_state() >= 0
    if newframe and draw:
        Frame_of_input = mkw_utils.frame_of_input()
        Angle_History.update()
        RaceComp_History.update()
        Pos_History.update()
        if maxLap == int(RaceManagerPlayer.race_completion_max(0))-1:
            mkw_utils.calculate_exact_finish(Pos_History, maxLap)
        maxLap = int(RaceManagerPlayer.race_completion_max(0))

    if draw:
        text = create_infodisplay(c, RaceComp_History, Angle_History)
    else:
        RaceComp_History.clear()
        Angle_History.clear()
        Pos_History.clear()
        text = ''

