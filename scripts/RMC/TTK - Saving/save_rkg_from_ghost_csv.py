from dolphin import gui, event, utils
from Modules import ttk_lib
import time

"""
save_rkg_from_ghost_csv

This script retrieves the inputs from the ghost csv and creates a ghost RKG file
"""

def main() -> None:
    gui.add_osd_message("Script started")
    
    # Get FrameSequence from csv
    input_sequence = ttk_lib.get_input_sequence_from_csv(ttk_lib.PlayerType.GHOST)
    
    if (input_sequence is None or len(input_sequence) == 0):
        gui.add_osd_message("No inputs read!")
        return
    
    ttk_lib.get_metadata_and_write_to_rkg(input_sequence, ttk_lib.PlayerType.GHOST)

if __name__ == '__main__':
    main()
    global script_end_time
    script_end_time = time.time()


@event.on_timertick
def cancel():
    if script_end_time and (time.time() - script_end_time > 0.2):
        utils.cancel_script(utils.get_script_name())
