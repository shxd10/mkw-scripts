"""
Usage: This script loops a sequence of inputs between two respawns.
The main purpose for this is to perform the Negative Lap Underflow glitch without the hassle of copying inputs and having a big CSV file.
Step 1: Start this script in-game
Step 2: If you now respawn, the script will start recording your inputs
Step 3: On your next respawn, the script will stop recording and start playing back your inputs infinitely
While it is recommended to directly TAS the recording of the inputs with the script on, you can also playback an already existing CSV file,
just make sure the actual inputs start on the frame the respawn counter ends.
To playback an existing segment of inputs, set the variable under this text to "True" and have the CSV file in the same folder as this script named "input_loop.csv".
"""
RECORD_EXISTING_INPUTS = False

import os # noqa: E402
from dolphin import event, gui, utils # type: ignore # noqa: E402
import Modules.mkw_classes as mkw # noqa: E402
from Modules import ttk_lib # noqa: E402
from Modules.mkw_utils import frame_of_input # noqa: E402
from Modules.framesequence import FrameSequence # noqa: E402

@event.on_savestateload
def on_state_load(is_slot, slot):
    global player_inputs
    player_inputs.read_from_file()

@event.on_framebegin
def on_frame_begin():
    global recording, playback, first_respawn, second_respawn, last_respawn_timer, player_inputs, segment, last_offset, segment_path, input_loop

    if mkw.RaceManager().state() != mkw.RaceState.RACE:
        return

    kart_collide = mkw.KartCollide()
    respawn_timer = kart_collide.time_before_respawn()
    frame = frame_of_input()

    if last_respawn_timer is not None and last_respawn_timer > 0 and respawn_timer == 0:
        if not recording and not playback:
            recording = True
            first_respawn = frame
            gui.add_osd_message("Recording started, next respawn will stop and play back", 5000)

        elif recording:
            recording = False
            playback = True
            second_respawn = frame

            player_inputs = ttk_lib.read_full_decoded_rkg_data(ttk_lib.PlayerType.PLAYER)
            if not player_inputs:
                gui.add_osd_message("No inputs read!", 5000)
                return

            segment = player_inputs.frames[first_respawn:second_respawn]

            fs = FrameSequence()
            fs.read_from_list_of_frames(segment)
            if fs.write_to_file(segment_path):
                gui.add_osd_message("Inputs written to {}".format(os.path.basename(segment_path)))
            else:
                gui.add_osd_message("{} is currently locked by another program.".format(os.path.basename(segment_path)))

            gui.add_osd_message(f"Playback started with {len(segment)} frames", 5000)

    last_respawn_timer = respawn_timer

    if RECORD_EXISTING_INPUTS and recording and not playback:
        input_loop_len = len(input_loop.frames)
        if input_loop and input_loop_len > 0:
            offset = (frame - first_respawn) % input_loop_len
            ttk_lib.write_player_inputs(input_loop[offset])
        if offset == 0 and last_offset != 0:
            gui.add_osd_message(f"Resuming previous loop with {input_loop_len} frames", 5000)
        
        last_offset = offset

    if playback and segment:
        segment_length = len(segment)
        if segment_length > 0:
            offset = (frame - first_respawn) % segment_length
            playback_input = segment[offset]
            ttk_lib.write_player_inputs(playback_input)

            if offset == 0 and last_offset != 0:
                gui.add_osd_message("Restarted loop", 2000)

            last_offset = offset

def main():
    global recording, playback, first_respawn, second_respawn, last_respawn_timer, player_inputs, segment, last_offset, segment_path, input_loop
    recording = False
    playback = False
    first_respawn = None
    second_respawn = None
    last_respawn_timer = None
    player_inputs = None
    segment = []
    last_offset = -1
    segment_path = os.path.join(os.path.dirname(utils.get_script_name()), "input_loop.csv")
    input_loop = FrameSequence(segment_path)
    gui.add_osd_message("Input recording will start on next respawn.", 5000)


if __name__ == "__main__":
    main()
