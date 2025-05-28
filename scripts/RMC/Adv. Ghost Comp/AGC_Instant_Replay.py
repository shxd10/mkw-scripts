from dolphin import event, gui, utils
from Modules import agc_lib as lib
from Modules import settings_utils as setting
from Modules.mkw_classes import RaceManager, RaceState
from Modules import mkw_utils as mkw_utils
import os
from math import floor

def main():

    global loaddatalist
    loaddatalist = {}
    
    global storedatalist
    storedatalist = {}

    global frame
    frame = mkw_utils.frame_of_input()
    
if __name__ == '__main__':
    main()


@event.on_frameadvance
def on_frame_advance():
    global frame

    if not (frame == mkw_utils.frame_of_input() or frame == mkw_utils.frame_of_input()-1):
        c = setting.get_agc_config()
        loaddatalist.clear()
        for key in storedatalist.keys():
            loaddatalist[key] = storedatalist[key]
        storedatalist.clear()

    
    racestate = RaceManager().state().value
    frame = mkw_utils.frame_of_input()

    
    if racestate >= RaceState.COUNTDOWN.value :
        if frame in loaddatalist.keys():
            loaddatalist[frame].load(1)

        storedatalist[frame] = lib.AGCFrameData()

    
    
