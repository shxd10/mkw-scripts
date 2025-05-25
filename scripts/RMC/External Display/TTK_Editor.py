from dolphin import event, utils # type: ignore
import os
import struct
import time
from external import external_utils as ex
from Modules import ttk_lib, rkg_lib
from Modules.framesequence import FrameSequence
from Modules.mkw_translations import course_slot_abbreviation
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
    with open(os.path.join(scriptDir, 'Modules', "default.mii"), 'rb') as f:
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

def open_player_editor():
    ex.open_file(player_inputs.filename)

def open_ghost_editor():
    ex.open_file(ghost_inputs.filename)

def csv_to_working_csv(target: ttk_lib.PlayerType):
    filetype = [('CSV files', '*.csv'), ('All files', '*')]
    scriptDir = utils.get_script_dir()
    ttkDir = os.path.join(utils.get_script_dir(), 'MKW_Inputs')
    file_path = ex.open_dialog_box(scriptDir, filetype, ttkDir, 'Open CSV')
    if not file_path:
        return
    
    input_sequence = FrameSequence(file_path)
    input_sequence.read_from_file()
    if input_sequence is None or len(input_sequence) == 0:
        return
    print(len(input_sequence))
    ttk_lib.write_to_csv(input_sequence, target)    

def save_csv_to_player():
    csv_to_working_csv(ttk_lib.PlayerType.PLAYER)

def save_csv_to_ghost():
    csv_to_working_csv(ttk_lib.PlayerType.GHOST)
    
# This constant determines the function that gets called by each button.
# The position of each function should match the corresponding button text in
# the other BUTTON_LAYOUT in `external/editor_window.py`
BUTTON_LAYOUT = [
    [
        [save_player_to_player_csv, save_ghost_to_player_csv],
        [save_player_csv_to_rkg, save_rkg_to_player_csv],
        [open_player_editor, save_csv_to_player]
    ],
    [
        [save_player_to_ghost_csv, save_ghost_to_ghost_csv],
        [save_ghost_csv_to_rkg, save_rkg_to_ghost_csv],
        [open_ghost_editor, save_csv_to_ghost],
    ],
]

def main():
    global shm_activate, shm_player_csv, shm_ghost_csv
    shm_activate = ex.SharedMemoryBlock.create(name="editor_activate", buffer_size=2)
    shm_player_csv = ex.SharedMemoryWriter(name="editor_player_csv", buffer_size=256)
    shm_ghost_csv = ex.SharedMemoryWriter(name="editor_ghost_csv", buffer_size=256)

    global player_inputs, ghost_inputs
    player_inputs = ttk_lib.get_input_sequence_from_csv(ttk_lib.PlayerType.PLAYER)
    ghost_inputs = ttk_lib.get_input_sequence_from_csv(ttk_lib.PlayerType.GHOST)
    shm_player_csv.write_text(player_inputs.filename)
    shm_ghost_csv.write_text(ghost_inputs.filename)

    ex.SharedMemoryBlock.create(name="editor_buttons", buffer_size=4)
    global shm_buttons
    shm_buttons = ex.SharedMemoryBlock.connect(name="editor_buttons")

    ex.SharedMemoryBlock.create(name="editor_window_closed", buffer_size=2)
    global shm_close
    shm_close = ex.SharedMemoryBlock.connect(name="editor_window_closed")

    # If a button function is executed immediately while emulation is not paused, it can cause
    # pycore to freeze. To avoid this, button events are stored in this queue. If emulation
    # is not paused, the event will be processed in `on_frame_advance` which won't freeze. If
    # emulation is paused, the event will be processed in `on_timertick`.
    global button_queue
    button_queue = []

    global prev_track, shm_frame_of_input
    prev_track = course_slot_abbreviation()
    shm_frame_of_input = ex.SharedMemoryWriter(name='editor_frame_of_input', buffer_size=256)

    window_script_path = os.path.join(utils.get_script_dir(), "external", "ttk_editor_window.py")
    #ex.start_external_script(window_script_path)


        
# Function that watches for button events
# This function should be called continuously:
# either `on_timertick` when the game is paused
# or `on_frameadvance` when the game isn't paused
def listen_for_buttons():

    # If window sent a button event, add it to queue
    button_event = shm_buttons.read()[:4]
    if button_event[0]:
        button_queue.append(button_event)
        shm_buttons.clear()

    if button_queue:
        execute_button_function()

    close_event = shm_close.read_text()
    if close_event == "1":
        utils.cancel_script(utils.get_script_name())
        shm_close.write_text('0')

# Helper that pops the oldest button event in the queue and executes it
def execute_button_function():
    button_event = button_queue.pop(0)
    section_index, row_index, col_index = struct.unpack('>BBB', button_event[1:4])
    try:
        BUTTON_LAYOUT[section_index][row_index][col_index]()
    except Exception as e:
        print(f"Error executing button function: {e}")


# Helper that reads state of activate checkboxes
def get_activation_state():
    return struct.unpack('>??', shm_activate.read())


def reload_inputs():
    global player_inputs
    global ghost_inputs
    
    player_inputs = ttk_lib.get_input_sequence_from_csv(ttk_lib.PlayerType.PLAYER)
    player_inputs.read_from_file()
    shm_player_csv.write_text(player_inputs.filename)
    
    ghost_inputs = ttk_lib.get_input_sequence_from_csv(ttk_lib.PlayerType.GHOST)
    ghost_inputs.read_from_file()
    shm_ghost_csv.write_text(ghost_inputs.filename)

        
@event.on_timertick
def on_timer_tick():
    #Only do stuff when the game is paused to avoid crashes
    if utils.is_paused():
        listen_for_buttons()

        
@event.on_savestateload
def on_state_load(is_slot, slot):
    reload_inputs()
    
@event.on_frameadvance
def on_frame_advance():
    global shm_frame_of_input
    current_frame = frame_of_input()
    shm_frame_of_input.write_text(str(current_frame))


@event.on_framebegin
def on_frame_begin():
    listen_for_buttons()

    global prev_track
    track = course_slot_abbreviation()
    if track != prev_track:
        reload_inputs()
    prev_track = track
        
    if RaceManager.state() not in (RaceState.COUNTDOWN, RaceState.RACE):
        return
    
    activate_player, activate_ghost = get_activation_state()
    frame = frame_of_input()
    
    if activate_player and player_inputs[frame]:
        ttk_lib.write_player_inputs(player_inputs[frame])
    
    if activate_ghost and ghost_inputs[frame]:
        ttk_lib.write_ghost_inputs(ghost_inputs[frame])


if __name__ == '__main__':
    main()
