"""
Writes infodisplay text to a shared memory buffer than can be accessed by external applications
"""
import os
from dolphin import event, utils, memory # type: ignore
from external import external_utils
import Modules.settings_utils as setting
import Modules.mkw_utils as mkw_utils
from Modules.infodisplay_utils import create_infodisplay
from Modules.mkw_classes import RaceManager, RaceManagerPlayer, RaceState, KartObjectManager, VehiclePhysics

from Modules.mkw_classes.common import SurfaceProperties, eulerAngle
from Modules.mkw_utils import History 

ROUND_DIGITS = 6
TEXT_COLOR = 0xFFFFFFFF

LAST_FRAME = {}


@event.on_frameadvance
def on_frame_advance():
    global Frame_of_input
    global Angle_History
    global RaceComp_History
    global c
    global special_event
    global maxLap

    
    race_mgr = RaceManager()
    newframe = Frame_of_input != mkw_utils.frame_of_input()
    draw = race_mgr.state().value >= RaceState.COUNTDOWN.value
    if newframe and draw:
        Frame_of_input = mkw_utils.frame_of_input()
        try:
            Angle_History.update()
            RaceComp_History.update()
            Pos_History.update()
            if maxLap == int(RaceManagerPlayer.race_completion_max(0))-1:
                mkw_utils.calculate_exact_finish(Pos_History, maxLap)
            maxLap = int(RaceManagerPlayer.race_completion_max(0))
        except AssertionError:
            pass
        
    global shm_writer
    
    if newframe:
        Frame_of_input = mkw_utils.frame_of_input()
    
    if draw:
        shm_writer.write_text(create_infodisplay(c, RaceComp_History, Angle_History))
    else:
        RaceComp_History.clear()
        Angle_History.clear()
        Pos_History.clear()


@event.on_savestateload
def on_state_load(fromSlot: bool, slot: int):
    global c
    c = setting.get_infodisplay_config()
    if memory.is_memory_accessible() and mkw_utils.extended_race_state() >= 0:
        shm_writer.write_text(create_infodisplay(c, RaceComp_History, Angle_History))


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

    global shm_writer
    shm_writer = external_utils.SharedMemoryWriter(name='infodisplay', buffer_size=4096)

    window_script_path = os.path.join(utils.get_script_dir(), "external", "info_display_window.py")
    external_utils.start_external_script(window_script_path)


if __name__ == '__main__':
    main()
