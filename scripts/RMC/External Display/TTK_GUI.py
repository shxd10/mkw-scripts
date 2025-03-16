from dolphin import event, gui, utils # type: ignore
import os
import struct
from external import external_utils as ex
from Modules import ttk_lib
from Modules.mkw_utils import frame_of_input
from Modules.framesequence import FrameSequence
from Modules.mkw_classes import RaceManager, RaceState
# from RMC.TTK_Saving import (
#     save_player_to_player_csv,
#     save_ghost_to_player_csv,
#     save_player_to_ghost_csv,
#     save_ghost_to_ghost_csv
# )


def save_player_to_player_csv():
    input_sequence = ttk_lib.read_full_decoded_rkg_data(ttk_lib.PlayerType.PLAYER)
    ttk_lib.write_to_csv(input_sequence, ttk_lib.PlayerType.PLAYER)
    gui.add_osd_message("Saved player to player CSV")

def save_ghost_to_player_csv():
    input_sequence = ttk_lib.read_full_decoded_rkg_data(ttk_lib.PlayerType.GHOST)
    ttk_lib.write_to_csv(input_sequence, ttk_lib.PlayerType.PLAYER)
    gui.add_osd_message("Saved ghost to player CSV")

def save_player_to_ghost_csv():
    input_sequence = ttk_lib.read_full_decoded_rkg_data(ttk_lib.PlayerType.PLAYER)
    ttk_lib.write_to_csv(input_sequence, ttk_lib.PlayerType.GHOST)
    gui.add_osd_message("Saved player to ghost CSV")

def save_ghost_to_ghost_csv():
    input_sequence = ttk_lib.read_full_decoded_rkg_data(ttk_lib.PlayerType.GHOST)
    ttk_lib.write_to_csv(input_sequence, ttk_lib.PlayerType.GHOST)
    gui.add_osd_message("Saved ghost to ghost CSV")


BUTTON_LAYOUT = [
    [
        [save_player_to_player_csv, save_ghost_to_player_csv],
    ],
    [
        [save_player_to_ghost_csv, save_ghost_to_ghost_csv],
    ],
]

def main():
    global shm_activate, shm_buttons
    shm_activate = ex.SharedMemoryBlock.create(name="ttk_gui_activate", buffer_size=2)
    shm_buttons = ex.SharedMemoryBlock.create(name="ttk_gui_buttons", buffer_size=4)

    global activate_player, activate_ghost
    activate_player = False
    activate_ghost = False

    global player_inputs, ghost_inputs
    player_inputs = ttk_lib.get_input_sequence_from_csv(ttk_lib.PlayerType.PLAYER)
    ghost_inputs = ttk_lib.get_input_sequence_from_csv(ttk_lib.PlayerType.GHOST)

    window_script_path = os.path.join(utils.get_script_dir(), "external", "ttk_gui_window.py")
    ex.start_external_script(window_script_path)


@event.on_savestateload
def on_state_load(is_slot, slot):
    if activate_player:
        player_inputs.read_from_file()
    if activate_ghost:
        ghost_inputs.read_from_file()


@event.on_frameadvance
def on_frame_advance():
    if RaceManager.state() not in (RaceState.COUNTDOWN, RaceState.RACE):
        return
    
    frame = frame_of_input()

    global activate_player, activate_ghost
    activate_player, activate_ghost = struct.unpack('>??', shm_activate.read())

    update, section_index, row_index, col_index = struct.unpack('>?BBB', shm_buttons.read())
    if update:
        print(section_index, row_index, col_index)
        BUTTON_LAYOUT[section_index][row_index][col_index]()
        shm_buttons.clear()
    
    if activate_player and player_inputs[frame]:
        ttk_lib.write_player_inputs(player_inputs[frame])
    
    if activate_ghost and ghost_inputs[frame]:
        ttk_lib.write_ghost_inputs(ghost_inputs[frame])


if __name__ == '__main__':
    main()