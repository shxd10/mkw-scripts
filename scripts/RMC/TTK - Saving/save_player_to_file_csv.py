from dolphin import gui, utils, event
from Modules import ttk_lib
from external import external_utils as ex
import os
import time

"""
save_player_to_player_csv

This script takes the player's inputs and writes them to the player csv
"""

def main() -> None:
    gui.add_osd_message("Script started")
    
    # Convert internal RKG to input list
    input_sequence = ttk_lib.read_full_decoded_rkg_data(ttk_lib.PlayerType.PLAYER)
    
    if (input_sequence is None or len(input_sequence) == 0):
        gui.add_osd_message("No inputs read!")
        return

    filetype = [('CSV files', '*.csv'), ('All files', '*')]
    scriptDir = utils.get_script_dir()
    ttk_dir = os.path.join(scriptDir, 'MKW_Inputs')
    write_file = ex.save_dialog_box(scriptDir, filetype, ttk_dir, 'Save as CSV File')
    
    if write_file:
        input_sequence.write_to_file(write_file)
    else:
        gui.add_osd_message("Save Aborted")

if __name__ == '__main__':
    main()
    global script_end_time
    script_end_time = time.time()


@event.on_timertick
def cancel():
    if script_end_time and (time.time() - script_end_time > 0.2):
        utils.cancel_script(utils.get_script_name())
