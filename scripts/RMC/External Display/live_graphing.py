import os
import struct
from dolphin import event, utils # type: ignore
from Modules import mkw_classes as mkw
from Modules import mkw_utils
from external import external_utils


def get_frame_data():
    frame = mkw_utils.frame_of_input()
    vehicle_physics = mkw.VehiclePhysics()
    ev = vehicle_physics.external_velocity()
    return struct.pack('>Iff', frame, ev.length(), ev.length_xz())


@event.on_frameadvance
def on_frame_advance():
    global shm_writer
    global in_race
    
    if mkw.RaceManager().state().value >= mkw.RaceState.COUNTDOWN.value:
        in_race = True
        shm_writer.write(get_frame_data())
    elif in_race:
        in_race = False
        shm_writer.write(b'\x00')


def main():
    global in_race
    in_race = False

    global shm_writer
    shm_writer = external_utils.SharedMemoryWriter(name='graphdata', buffer_size=32)

    window_script_path = os.path.join(utils.get_script_dir(), "external", "live_graphing_window.py")
    external_utils.start_external_script(window_script_path)


if __name__ == '__main__':
    main()
