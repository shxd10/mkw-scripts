from dolphin import event, gui, utils
import configparser
import Modules.agc_lib as lib
import Modules.settings_utils as setting
from Modules.mkw_classes import RaceManager, RaceState
import Modules.mkw_utils as mkw_utils
import os


def main():
    global c
    c = setting.get_agc_config()
    
    global filename
    filename = os.path.join(utils.get_script_dir(), c.ghost_path)

    global framedatalist
    framedatalist = {}

    global frame
    frame = mkw_utils.frame_of_input()
    
    global end
    end = False

    global metadata
    metadata = lib.AGCMetaData(read_id = 0)

@event.on_scriptend
def save(id_):
    if utils.get_script_id() == id_:
        
        lib.framedatalist_to_file(filename, framedatalist, metadata)
        print("saved data")
    

@event.on_frameadvance
def on_frame_advance():
    global framedatalist
    global end
    global frame
    global c
    global metadata
    metadata = lib.AGCMetaData(read_id = 0)

    if not (frame == mkw_utils.frame_of_input() or frame == mkw_utils.frame_of_input()-1):
        c = setting.get_agc_config()
    frame = mkw_utils.frame_of_input()
        
    racestate = RaceManager().state().value
    
    if (not end) and RaceState.RACE.value >= racestate >= RaceState.COUNTDOWN.value:
        framedatalist[frame] = lib.AGCFrameData()
        
    if (not end) and racestate == RaceState.FINISHED_RACE.value:
        end = True
        utils.cancel_script(utils.get_script_name())
        
        



if __name__ == '__main__':
    main()   
