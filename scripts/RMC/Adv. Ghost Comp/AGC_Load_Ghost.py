from dolphin import event, gui, utils
import Modules.agc_lib as lib
from Modules.mkw_classes import RaceManager, RaceState
import Modules.mkw_utils as mkw_utils
import os
from math import floor

def main():
    global filename
    filename = os.path.join(utils.get_script_dir(), r'AGC_Data\ghost_data.agc')

    global delay
    delay = 0

    global framedatalist
    global metadata

    metadata, framedatalist = lib.file_to_framedatalist(filename)

    
if __name__ == '__main__':
    main()


@event.on_frameadvance
def on_frame_advance():
    global metadata
    global framedatalist
    global delay
    
    racestate = RaceManager().state().value
    frame = mkw_utils.frame_of_input()
    delayed_frame = floor(delay)+frame
    decimal_delay = delay - floor(delay)

    metadata.load(1) #Force the ghost's combo and drift type
        
    if not mkw_utils.is_single_player():
        if racestate >= RaceState.COUNTDOWN.value :

            metadata.delay_timer(delay)
            
            if 0 < delayed_frame+1 < len(framedatalist):
                f1 = lib.AGCFrameData.read_from_string(str(framedatalist[delayed_frame])) #Makes a copy so you can modify f1 without affecting the framedatalist
                f2 = framedatalist[delayed_frame+1]
                f1.interpolate(f2, 1-decimal_delay, decimal_delay)
                f1.load(1)
    

