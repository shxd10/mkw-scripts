from dolphin import gui, utils, event, memory
from Modules import ttk_lib
from Modules import agc_lib
from Modules import mkw_utils
from Modules.mkw_classes import RaceManager, RaceState
from external import external_utils as ex
from Modules.rkg_lib import decode_RKG
import os
import sys


"""
save_player_to_player_csv

This script takes the player's inputs and writes them to the player csv
"""

def main() -> None:
    gui.add_osd_message("Script started")
    global agc_metadata
    global input_sequence
    global end
    
    #Prompt the user to select a .rkg file
    filetype = [('RKG files', '*.rkg'), ('All files', '*')]
    scriptDir = utils.get_script_dir()
    ghostDir = os.path.join(scriptDir, 'Ghost')
    
    file_path = ex.open_dialog_box(scriptDir, filetype, '', 'Open a RKG File')

    with open(file_path, 'rb') as f:
        metadata, input_sequence, mii_data = decode_RKG(f.read())
        
    agc_metadata = agc_lib.AGCMetaData.read_from_RKGMetadata(metadata)
    
    if input_sequence:
        end = False
        if not mkw_utils.is_single_player():
            if RaceManager().state().value > 0:
                ttk_lib.write_inputs_to_current_ghost_rkg(input_sequence)
                agc_metadata.delay_timer(0)
    else:
        end = True
    
if __name__ == '__main__':
    main()

@event.on_savestateload
def on_state_load(is_slot, slot):
    if memory.is_memory_accessible() and not mkw_utils.is_single_player():
        ttk_lib.write_inputs_to_current_ghost_rkg(input_sequence)
        agc_metadata.delay_timer(0)
    
    
@event.on_frameadvance
def on_frame_advance():
    global agc_metadata
    global input_sequence
    global end

    if not end:
        racestate = RaceManager().state().value

        agc_metadata.load(1) 
            
        if not mkw_utils.is_single_player():
            if racestate == RaceState.COUNTDOWN.value :
                ttk_lib.write_inputs_to_current_ghost_rkg(input_sequence)
                agc_metadata.delay_timer(0)
    
            

    
