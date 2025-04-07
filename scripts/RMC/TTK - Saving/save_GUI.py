from dolphin import gui, utils, memory, event
from Modules import ttk_lib
from external import external_utils as ex
from Modules.rkg_lib import decode_RKG, encode_RKG, RKGMetaData
from Modules.framesequence import FrameSequence
import os
import sys
import time



def main() -> None:
    gui.add_osd_message("Script started")

    scriptDir = utils.get_script_dir()
    scriptname = os.path.join(scriptDir, 'external', 'TTK_Save_GUI_window.py')
    
    std = ex.run_external_script(scriptname)
    args = std.split('\n')[0].split('|')

    if len(args) > 1:
        if args[0] == 'Player Inputs':
            inputs = ttk_lib.read_full_decoded_rkg_data(ttk_lib.PlayerType.PLAYER)
        elif args[0] == 'Ghost Inputs':
            inputs = ttk_lib.read_full_decoded_rkg_data(ttk_lib.PlayerType.GHOST)
        elif args[0] == 'CSV Player':
            inputs = ttk_lib.get_input_sequence_from_csv(ttk_lib.PlayerType.PLAYER)
            inputs.read_from_file()
        elif args[0] == 'CSV Ghost':
            inputs = ttk_lib.get_input_sequence_from_csv(ttk_lib.PlayerType.GHOST)
            inputs.read_from_file()
        else:
            if args[0][-4:] == ".rkg":
                with open(args[0], "rb") as f:
                    inputs = decode_RKG(f.read())[1]
            elif args[0][-4:] == ".csv":
                inputs = FrameSequence(args[0])
                inputs.read_from_file()
            else:
                raise ValueError('Invalid source file')

    with open(os.path.join(scriptDir, 'Ghost', 'Default', "default.mii"), 'rb') as f:
        mii_data = f.read()[:0x4A]
    
    for i in range(1, len(args)):
        arg = args[i]
        if arg == 'csv_player':
            ttk_lib.write_to_csv(inputs, ttk_lib.PlayerType.PLAYER)
        elif arg == 'csv_ghost':
            ttk_lib.write_to_csv(inputs, ttk_lib.PlayerType.GHOST)
        elif arg[-4:] == ".rkg":
            with open(arg, "wb") as f:
                f.write(encode_RKG(RKGMetaData.from_current_race(), inputs, mii_data))
        elif arg[-4:] == ".csv":
            inputs.write_to_file(arg)



if __name__ == '__main__':
    main()
    global script_end_time
    script_end_time = time.time()


@event.on_timertick
def cancel():
    if script_end_time and (time.time() - script_end_time > 0.2):
        utils.cancel_script(utils.get_script_name())
