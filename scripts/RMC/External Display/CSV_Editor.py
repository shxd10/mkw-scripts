from dolphin import utils, event # type: ignore
from external import external_utils as ex
from Modules import ttk_config, mkw_utils, mkw_translations, ttk_lib
import os

@event.on_frameadvance
def on_frame_advance():
    global shm_frame_of_input
    current_frame = mkw_utils.frame_of_input()
    shm_frame_of_input.write_text(str(current_frame))
    
@event.on_framebegin
def on_frame_begin():
    global prev_track, player_inputs, ghost_inputs
    track = mkw_translations.course_slot_abbreviation()
    if track != prev_track:
        player_inputs = ttk_lib.get_input_sequence_from_csv(ttk_lib.PlayerType.PLAYER)
        shm_player_csv.write_text(player_inputs.filename)
        
        ghost_inputs = ttk_lib.get_input_sequence_from_csv(ttk_lib.PlayerType.GHOST)
        shm_ghost_csv.write_text(ghost_inputs.filename)
        print(player_inputs.filename)
        print("Reloaded inputs")
    prev_track = track
    
def main():
    global shm_frame_of_input, shm_player_csv, shm_ghost_csv, player_inputs, ghost_inputs, prev_track
    shm_frame_of_input = ex.SharedMemoryWriter(name='editor_frame_of_input', buffer_size=256)
    shm_player_csv = ex.SharedMemoryWriter(name="editor_player_csv", buffer_size=256)
    shm_ghost_csv = ex.SharedMemoryWriter(name="editor_ghost_csv", buffer_size=256)
    
    player_inputs = ttk_lib.get_input_sequence_from_csv(ttk_lib.PlayerType.PLAYER)
    ghost_inputs = ttk_lib.get_input_sequence_from_csv(ttk_lib.PlayerType.GHOST)
    prev_track = mkw_translations.course_slot_abbreviation()
    
    shm_player_csv.write_text(player_inputs.filename)
    shm_ghost_csv.write_text(ghost_inputs.filename)
    
    #ex.start_external_script(os.path.join(utils.get_script_dir(), "external", "csv_editor_window.py"))


if __name__ == '__main__':
    main()
    
    
