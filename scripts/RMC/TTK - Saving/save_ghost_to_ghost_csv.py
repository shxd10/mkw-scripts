from dolphin import gui, utils, event
from Modules import ttk_lib
import time

"""
save_ghost_to_ghost_csv

This script takes the current ghost's inputs and write them to the ghost csv file
"""

def main() -> None:
    gui.add_osd_message("Script started")
    
    # Convert internal RKG to input list
    input_sequence = ttk_lib.read_full_decoded_rkg_data(ttk_lib.PlayerType.GHOST)
    
    if (input_sequence is None or len(input_sequence) == 0):
        gui.add_osd_message("No inputs read!")
        return
    
    ttk_lib.write_to_csv(input_sequence, ttk_lib.PlayerType.GHOST)

if __name__ == '__main__':
    main()
    global script_end_time
    script_end_time = time.time()


@event.on_timertick
def cancel():
    if script_end_time and (time.time() - script_end_time > 0.2):
        utils.cancel_script(utils.get_script_name())
