from dolphin import event, gui, utils
import configparser
import math
import os

from Modules.mkw_classes.common import SurfaceProperties, eulerAngle
from Modules.mkw_utils import History 

from external.external_utils import run_external_script
import Modules.settings_utils as setting
import Modules.mkw_utils as mkw_utils
from Modules.infodisplay_utils import draw_infodisplay, draw_infodisplay_fr, special
from Modules.mkw_classes import RaceManager, RaceManagerPlayer, RaceState






@event.on_savestateload
def on_state_load(fromSlot: bool, slot: int):
    global c
    race_mgr = RaceManager()
    c = setting.get_infodisplay_config()
    
    '''if race_mgr.state().value >= RaceState.COUNTDOWN.value:
        text = create_infodisplay()
        gui.draw_text((10, 10), c.color, text)'''
    

 # Something in that commented code causes dolphin to crash when loading a savestate from boot to in race
 # It's the create_infodisplay, but I can't figure out a line that makes the crash.
 # I think it's when there is too much instructions

    

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

    global special_event
    special_event = (False,False)


if __name__ == '__main__':
    main()


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

    if draw:
        if not special():
            draw_infodisplay(c, RaceComp_History, Angle_History)
        else:
            if Frame_of_input>240 and not special_event[0]:
                special_event = (True, run_external_script(os.path.join(utils.get_script_dir(), 'external', 'special.py')).split('\n')[-1] == 'w')
            if Frame_of_input<=240 or special_event[1]:
                draw_infodisplay(c, RaceComp_History, Angle_History)
            else:
                draw_infodisplay_fr(c, RaceComp_History, Angle_History)

