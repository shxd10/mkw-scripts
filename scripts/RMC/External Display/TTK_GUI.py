from dolphin import event, gui, utils # type: ignore
import os
import struct
import time
import threading
from external import external_utils as ex
from Modules import ttk_lib, rkg_lib
from Modules.mkw_utils import frame_of_input
from Modules.mkw_classes import RaceManager, RaceState

PLAYER_STR = ["player", "ghost"]

# Button functions

def game_to_working_csv(source: ttk_lib.PlayerType, target: ttk_lib.PlayerType):
    input_sequence = ttk_lib.read_full_decoded_rkg_data(source)
    if not (input_sequence is None or len(input_sequence) == 0):
        ttk_lib.write_to_csv(input_sequence, target)

def save_player_to_player_csv():
    game_to_working_csv(ttk_lib.PlayerType.PLAYER, ttk_lib.PlayerType.PLAYER)

def save_ghost_to_player_csv():
    game_to_working_csv(ttk_lib.PlayerType.GHOST, ttk_lib.PlayerType.PLAYER)

def save_player_to_ghost_csv():
    game_to_working_csv(ttk_lib.PlayerType.PLAYER, ttk_lib.PlayerType.GHOST)

def save_ghost_to_ghost_csv():
    game_to_working_csv(ttk_lib.PlayerType.GHOST, ttk_lib.PlayerType.GHOST)


def working_csv_to_rkg(source: ttk_lib.PlayerType):
    input_sequence = ttk_lib.get_input_sequence_from_csv(source)
    if input_sequence is None or len(input_sequence) == 0:
        return
    
    filetype = [('RKG files', '*.rkg'), ('All files', '*')]
    scriptDir = utils.get_script_dir()
    ghostDir = os.path.join(utils.get_script_dir(), 'Ghost')
    with open(os.path.join(scriptDir, 'Ghost', 'Default', "default.mii"), 'rb') as f:
        mii_data = f.read()[:0x4A]

    file_path = ex.save_dialog_box(scriptDir, filetype, ghostDir, 'Save RKG')
    if not file_path:
        return
    with open(file_path, "wb") as f:
        f.write(rkg_lib.encode_RKG(rkg_lib.RKGMetaData.from_current_race(), input_sequence, mii_data))


def save_player_csv_to_rkg():
    working_csv_to_rkg(ttk_lib.PlayerType.PLAYER)

def save_ghost_csv_to_rkg():
    working_csv_to_rkg(ttk_lib.PlayerType.GHOST)


def rkg_to_working_csv(target: ttk_lib.PlayerType):
    filetype = [('RKG files', '*.rkg'), ('All files', '*')]
    scriptDir = utils.get_script_dir()
    ghostDir = os.path.join(utils.get_script_dir(), 'Ghost')
    file_path = ex.open_dialog_box(scriptDir, filetype, ghostDir, 'Open RKG')
    if not file_path:
        return
    
    with open(file_path, 'rb') as f:
        rkg_data = rkg_lib.decode_RKG(f.read())
    input_sequence = None if rkg_data is None else rkg_data[1]
    if input_sequence is None or len(input_sequence) == 0:
        return
    ttk_lib.write_to_csv(input_sequence, target)


def save_rkg_to_player_csv():
    rkg_to_working_csv(ttk_lib.PlayerType.PLAYER)

def save_rkg_to_ghost_csv():
    rkg_to_working_csv(ttk_lib.PlayerType.GHOST)


# This constant determines the function that gets called by each button.
# The position of each function should match the corresponding button text in
# the other BUTTON_LAYOUT in `external/ttk_gui_window.py`
BUTTON_LAYOUT = [
    [
        [save_player_to_player_csv, save_ghost_to_player_csv],
        [save_player_csv_to_rkg, save_rkg_to_player_csv],
    ],
    [
        [save_player_to_ghost_csv, save_ghost_to_ghost_csv],
        [save_ghost_csv_to_rkg, save_rkg_to_ghost_csv]
    ],
]

def main():
    global shm_activate, shm_player_csv, shm_ghost_csv
    shm_activate = ex.SharedMemoryBlock.create(name="ttk_gui_activate", buffer_size=2)
    shm_player_csv = ex.SharedMemoryWriter(name="ttk_gui_player_csv", buffer_size=256)
    shm_ghost_csv = ex.SharedMemoryWriter(name="ttk_gui_ghost_csv", buffer_size=256)

    global player_inputs, ghost_inputs
    player_inputs = ttk_lib.get_input_sequence_from_csv(ttk_lib.PlayerType.PLAYER)
    ghost_inputs = ttk_lib.get_input_sequence_from_csv(ttk_lib.PlayerType.GHOST)
    shm_player_csv.write_text(player_inputs.filename)
    shm_ghost_csv.write_text(ghost_inputs.filename)

    window_script_path = os.path.join(utils.get_script_dir(), "external", "ttk_gui_window.py")
    ex.start_external_script(window_script_path)

    # Handle button events in a separate thread
    global button_queue
    button_queue = []

    ex.SharedMemoryBlock.create(name="ttk_gui_buttons", buffer_size=4)

    current_thread = threading.current_thread()
    listener_thread = threading.Thread(target=listen_for_buttons, args=(current_thread,))
    listener_thread.start()


# This gets run in a different thread to prevent blocking
def listen_for_buttons(parent: threading.Thread):
    BUTTON_WAIT = 1
    shm_buttons = ex.SharedMemoryBlock.connect(name="ttk_gui_buttons")

    while parent.is_alive():
        # If window sent button data, add it to queue
        button_data = shm_buttons.read()[:4]
        if button_data[0]:
            button_queue.append({'data': button_data, 'time': time.time()})
            shm_buttons.clear()

        # If oldest button data has been in queue longer than BUTTON_WAIT, assume 
        # emulation is paused and execute button function without waiting for next frame
        if button_queue and (time.time() - button_queue[0]['time'] > BUTTON_WAIT):
            execute_button_function()

        time.sleep(0.01)  # Prevents CPU hogging


# Helper that pops the oldest button command in the queue and executes it
def execute_button_function():
    button_data = button_queue.pop(0)['data']
    section_index, row_index, col_index = struct.unpack('>BBB', button_data[1:4])
    try:
        BUTTON_LAYOUT[section_index][row_index][col_index]()
    except Exception as e:
        print(f"Error executing button function: {e}")


# Helper that reads state of activate checkboxes
def get_activation_state():
    return struct.unpack('>??', shm_activate.read())


@event.on_savestateload
def on_state_load(is_slot, slot):
    activate_player, activate_ghost = get_activation_state()
    if activate_player:
        player_inputs.read_from_file()
        shm_player_csv.write_text(player_inputs.filename)
    if activate_ghost:
        ghost_inputs.read_from_file()
        shm_ghost_csv.write_text(ghost_inputs.filename)


@event.on_frameadvance
def on_frame_advance():
    if RaceManager.state() not in (RaceState.COUNTDOWN, RaceState.RACE):
        return
    
    activate_player, activate_ghost = get_activation_state()
    frame = frame_of_input()
    
    if activate_player and player_inputs[frame]:
        ttk_lib.write_player_inputs(player_inputs[frame])
    
    if activate_ghost and ghost_inputs[frame]:
        ttk_lib.write_ghost_inputs(ghost_inputs[frame])

    # If button queue is not empty, execute oldest button function
    if button_queue:
        execute_button_function()


if __name__ == '__main__':
    main()