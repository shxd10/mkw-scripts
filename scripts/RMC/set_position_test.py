from dolphin import event, savestate # type: ignore
from Modules import mkw_classes as mkw, mkw_utils
from Modules.mkw_classes.common import vec3
import math

START_FRAME = 1088
TEST_FRAME = 1098

class State:
    def __init__(self):
        self.savestate = None
        self.iteration = 0
    
    def set(self):
        if self.savestate is None:
            self.savestate = savestate.save_to_bytes()
    
    def load(self):
        self.iteration += 1
        savestate.load_from_bytes(self.savestate)

state = State()


def get_target_position(initial_pos: vec3):
    range_size = 10
    step_size = 1
    x_range = range(initial_pos.x - range_size, initial_pos.x + range_size, step_size)
    z_range = range(initial_pos.z - range_size, initial_pos.z + range_size, step_size)
    yield from iter(vec3(x, initial_pos.y, z) for x in x_range for z in z_range)


def run_test():
    ...


@event.on_frameadvance
def on_frame_advance():
    frame = mkw_utils.frame_of_input()
 
    if frame == START_FRAME - 1:
        state.set()
    
    if frame == START_FRAME:
        new_position = next(get_target_position(mkw.VehiclePhysics.position()))
        new_position.write(mkw.VehiclePhysics.chain() + 0x68)
    
    if frame == TEST_FRAME:
        speed = mkw.KartMove.speed()
        print(f"  Speed: {speed:.4f}")
        if speed < 5 or mkw.KartState.hwg_timer() == 0:
            print("  FAILED")
            state.load()
