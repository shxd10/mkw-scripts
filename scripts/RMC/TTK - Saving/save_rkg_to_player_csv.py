from dolphin import gui, utils
from Modules import ttk_lib
import os
import tkinter as tk
from tkinter import filedialog
import sys


"""
save_player_to_player_csv

This script takes the player's inputs and writes them to the player csv
"""

def main() -> None:
    gui.add_osd_message("Script started")
    print(sys.version_info)
    
    #Prompt the user to select a .rkg file
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(title = "Select a ghost file",
                                           filetypes = (('RKG files', '*.rkg'), ('All files', '*')),
                                           initialdir= os.path.join(utils.get_script_dir(), Ghost))
    with open(file_path, 'rb') as f:
        input_sequence = decode_RKG(f.read())
    
    if (input_sequence is None or len(input_sequence) == 0):
        gui.add_osd_message("No inputs read!")
        return
    
    ttk_lib.write_to_csv(input_sequence, ttk_lib.PlayerType.PLAYER)

if __name__ == '__main__':
    main()
