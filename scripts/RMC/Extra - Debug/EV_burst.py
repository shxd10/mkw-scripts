from dolphin import event, savestate, utils
import os
from pathlib import Path
from Modules import mkw_utils as mkw_utils
from Modules import framesequence as framesequence
from Modules import ttk_lib as ttk_lib
from Modules.mkw_translations import vehicle_id
from Modules import mkw_classes as mkw 

import time

def main():
    #savestate.load_from_slot(2)

    mkw_utils.add_angular_ev(0, 0, 10, 0)
    global end
    end = False




@event.on_frameadvance
def frameadvance():
    global end
    global g_save_file_name
   
    if (not end) and mkw_utils.extended_race_state() > 0:
        utils.cancel_script(utils.get_script_name())
        end = True



if __name__ == '__main__':
    main()
