from dolphin import gui, utils, event
from Modules import ttk_lib
from external import external_utils as ex
from Modules.rkg_lib import decode_RKG
import os
import sys
import time


"""
save_player_to_player_csv

This script takes the player's inputs and writes them to the player csv
"""

def main() -> None:
    gui.add_osd_message("Script started")

    #Prompt the user to select a .rkg file
    filetype = [('RKG files', '*.rkg'), ('All files', '*')]
    scriptDir = utils.get_script_dir()
    ghostDir = os.path.join(scriptDir, 'Ghost')
    
    file_path = ex.open_dialog_box(scriptDir, filetype, ghostDir, 'Open a RKG File')

    if not file_path:
        gui.add_osd_message("No file selected!")
        return
    
    with open(file_path, 'rb') as f:
        input_sequence = decode_RKG(f.read())[1]
    
    if (input_sequence is None or len(input_sequence) == 0):
        gui.add_osd_message("No inputs read!")
        return
    
    ttk_lib.write_to_csv(input_sequence, ttk_lib.PlayerType.PLAYER)

if __name__ == '__main__':
    main()
    global script_end_time
    script_end_time = time.time()


@event.on_timertick
def cancel():
    if script_end_time and (time.time() - script_end_time > 0.2):
        utils.cancel_script(utils.get_script_name())
