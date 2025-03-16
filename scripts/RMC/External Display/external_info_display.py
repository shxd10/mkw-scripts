"""
Writes infodisplay text to a shared memory buffer than can be accessed by external applications
"""
import os
from dolphin import event, utils # type: ignore
from external import external_utils
import Modules.settings_utils as setting
import Modules.mkw_utils as mkw_utils
from Modules.infodisplay_utils import create_infodisplay
from Modules.mkw_classes import RaceManager, RaceManagerPlayer, RaceState

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

    if not (Frame_of_input == mkw_utils.frame_of_input() or Frame_of_input == mkw_utils.frame_of_input()-1):
        c = setting.get_infodisplay_config()
    
    race_mgr = RaceManager()
    newframe = Frame_of_input != mkw_utils.frame_of_input()
    draw = race_mgr.state().value >= RaceState.COUNTDOWN.value
    if newframe and draw:
        Frame_of_input = mkw_utils.frame_of_input()
        try:
            Angle_History.update()
            RaceComp_History.update()
        except AssertionError:
            pass
        
    global shm_writer
    
    if newframe:
        Frame_of_input = mkw_utils.frame_of_input()
    
    if draw:
        shm_writer.write_text(create_infodisplay(c, RaceComp_History, Angle_History))


@event.on_savestateload
def on_state_load(fromSlot: bool, slot: int):
    global c
    c = setting.get_infodisplay_config()


def main():
    global c
    c = setting.get_infodisplay_config()

    global Frame_of_input
    Frame_of_input = 0

    def prc():
        return RaceManagerPlayer(0).race_completion()
    def grc():
        return RaceManagerPlayer(1).race_completion()
    def fa():
        return mkw_utils.get_facing_angle(0)
    def ma():
        return mkw_utils.get_moving_angle(0)
    
    global RaceComp_History
    RaceComp_History = History({'prc':prc, 'grc':grc}, c.history_size)

    global Angle_History
    Angle_History = History({'facing' : fa, 'moving' : ma}, 2)

    global shm_writer
    shm_writer = external_utils.SharedMemoryWriter(name='infodisplay', buffer_size=4096)

    window_script_path = os.path.join(utils.get_script_dir(), "external", "info_display_window.py")
    external_utils.start_external_script(window_script_path)


if __name__ == '__main__':
    main()
