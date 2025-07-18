from dolphin import event, gui, utils
from Modules import agc_lib as lib
from Modules import settings_utils as setting
from Modules.mkw_classes import RaceManager, RaceState
from Modules import mkw_utils as mkw_utils
import os
from math import floor

def main():
    global c
    c = setting.get_agc_config()
    
    global filename
    filename = os.path.join(utils.get_script_dir(), c.player_path)

    global framedatalist
    global metadata
    metadata, framedatalist = lib.file_to_framedatalist(filename)

    global frame
    frame = mkw_utils.frame_of_input()


@event.on_savestateload
def reload_config(_,__):
    global c
    c = setting.get_agc_config()

if __name__ == '__main__':
    main()


@event.on_frameadvance
def on_frame_advance():
    global metadata
    global framedatalist
    global c
    global frame

    delay = c.player_delay
    if not c.useFrames:
        delay *= mkw_utils.fps_const
    
    racestate = RaceManager().state().value
    frame = mkw_utils.frame_of_input()
    delayed_frame = floor(delay)+frame
    decimal_delay = delay - floor(delay)

        
    if racestate >= RaceState.COUNTDOWN.value :
        
        if 0 < delayed_frame+1 < len(framedatalist):
            f1 = lib.AGCFrameData.read_from_string(str(framedatalist[delayed_frame])) #Makes a copy so you can modify f1 without affecting the framedatalist
            f2 = framedatalist[delayed_frame+1]
            f1.interpolate(f2, 1-decimal_delay, decimal_delay)
            f1.load(0)
            f2.load(0, True)
    

