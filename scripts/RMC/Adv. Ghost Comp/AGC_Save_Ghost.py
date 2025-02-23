from dolphin import event, gui, utils
import Modules.agc_lib as lib
from Modules.mkw_classes import RaceManager, RaceState
import Modules.mkw_utils as mkw_utils
import os


def main():
    global filename
    filename = os.path.join(utils.get_script_dir(), r'AGC_Data\ghost_data.agc')

    global framedatalist
    framedatalist = {}

    global end
    end = False
    
if __name__ == '__main__':
    main()


@event.on_frameadvance
def on_frame_advance():
    global framedatalist
    global end
    
    racestate = RaceManager().state().value
    frame = mkw_utils.frame_of_input()
    
    if (not end) and RaceState.RACE.value >= racestate >= RaceState.COUNTDOWN.value:
        framedatalist[frame] = lib.AGCFrameData()
        
    if (not end) and racestate == RaceState.FINISHED_RACE.value:
        lib.framedatalist_to_file(filename, framedatalist, 0)
        end = True
    
    
